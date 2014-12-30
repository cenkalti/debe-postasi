from datetime import datetime, timedelta

import requests

import app
import debe

yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()[:10]
key = "debe-%s" % yesterday
content = app.mc.get(key)
if not content:
    print("no content")
    content = debe.generate_html().encode("utf-8")
    app.mc.set(key, content, time=24*60*60)

url = "https://api.mailgun.net/v2/%s/messages" % app.MAILGUN_DOMAIN
auth = ("api", app.MAILGUN_API_KEY)
response = requests.post(url, auth=auth, data={
    "from": "debe postasi <debe.postasi@gmail.com>",
    "to": app.MAILGUN_MAILING_LIST,
    "subject": "debe (%s)" % yesterday,
    "html": content,
})

assert response.status_code == 200, response.text
