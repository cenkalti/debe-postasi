import os
import json
from datetime import datetime

import pylibmc
import requests
from flask import Flask, request, abort

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
assert MAILGUN_API_KEY

MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
assert MAILGUN_DOMAIN

MAILGUN_MAILING_LIST = os.getenv("MAILGUN_MAILING_LIST")
assert MAILGUN_MAILING_LIST

SECRET = os.getenv("SECRET")
assert SECRET

mc = pylibmc.Client(os.getenv('MEMCACHEDCLOUD_SERVERS', '').split(','),
                    binary=True,
                    username=os.getenv('MEMCACHEDCLOUD_USERNAME'),
                    password=os.getenv('MEMCACHEDCLOUD_PASSWORD'),
                    behaviors={"tcp_nodelay": True,
                               "ketama": True,
                               "no_block": True})

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


@app.route("/cache/view")
def cache_view():
    if request.args["secret"] != SECRET:
        abort(403)
    return mc.get("debe") or "no debe in cache"


@app.route("/cache/clear")
def cache_clear():
    if request.args["secret"] != SECRET:
        abort(403)
    mc.delete("debe")
    return "cleared"


if __name__ == "__main__":
    app.run(debug=True)
