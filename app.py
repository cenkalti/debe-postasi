import os
import json
from datetime import datetime, timedelta

import bmemcached
import requests
from flask import Flask, request, abort

import debe

is_prod = bool(os.getenv("DYNO"))

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
if is_prod:
    assert MAILGUN_API_KEY

MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
if is_prod:
    assert MAILGUN_DOMAIN

MAILGUN_MAILING_LIST = os.getenv("MAILGUN_MAILING_LIST")
if is_prod:
    assert MAILGUN_MAILING_LIST

SECRET = os.getenv("SECRET")
if is_prod:
    assert SECRET


mc = bmemcached.Client(
        os.environ.get('MEMCACHEDCLOUD_SERVERS', '').split(','),
        os.environ.get('MEMCACHEDCLOUD_USERNAME'),
        os.environ.get('MEMCACHEDCLOUD_PASSWORD'))

app = Flask(__name__, static_folder="")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/kayit", methods=["POST"])
def kayit():
    url = "https://api.mailgun.net/v2/lists/%s/members" % MAILGUN_MAILING_LIST
    auth = ("api", MAILGUN_API_KEY)
    response = requests.post(url, auth=auth, data={
        "subscribed": "True",
        "address": request.form["email"],
        "vars": json.dumps({"date": datetime.utcnow().isoformat()[:19]}),
    })
    if response.status_code == 200:
        return "tamamdır."
    elif response.status_code == 400:
        return response.text
    else:
        raise Exception(response.text)


@app.route("/cache/generate")
def cache_generate():
    if request.args["secret"] != SECRET:
        abort(403)

    content = debe.generate_html()
    app.mc.set(get_subject(), content.encode(), time=24*60*60)
    return content


@app.route("/cache/view")
def cache_view():
    if request.args["secret"] != SECRET:
        abort(403)

    content = mc.get(get_subject())
    if not content:
        abort(404)

    return content.decode()


@app.route("/cache/clear")
def cache_clear():
    if request.args["secret"] != SECRET:
        abort(403)

    mc.delete(get_subject())
    return "cleared"


def get_subject():
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()[:10]
    return "debe (%s)" % yesterday


@app.cli.command()
def postala():
    key = get_subject()
    content = mc.get(key)
    if not content:
        content = debe.generate_html().encode("utf-8")
        mc.set(key, content, time=24*60*60)

    url = "https://api.mailgun.net/v2/%s/messages" % app.MAILGUN_DOMAIN
    auth = ("api", app.MAILGUN_API_KEY)
    response = requests.post(url, auth=auth, data={
        "from": "debe postasi <debe.postasi@gmail.com>",
        "to": app.MAILGUN_MAILING_LIST,
        "subject": key,
        "html": content,
    })

    assert response.status_code == 200, response.text


if __name__ == "__main__":
    app.run(debug=True)
