from datetime import datetime, timedelta

import requests

import config
import debe

content = debe.generate_html().encode("utf-8")
# print(content)

today = datetime.utcnow()
yesterday = today - timedelta(days=1)
# response = requests.post("http://httpbin.org/post", data={
response = requests.post(config.SENDLOOP_BASE_URL + "/Campaign.Create/json", data={
    "APIKey": config.SENDLOOP_API_KEY,
    "CampaignName": "debe-" + today.isoformat()[:10],
    "FromName": "debe postası",
    "FromEmail": "debe.postasi@gmail.com",
    "ReplyToName": "debe postası",
    "ReplyToEmail": "debe.postasi@gmail.com",
    "TargetListIDs[0]": config.SENDLOOP_LIST_ID,
    "Subject": "debe (%s)" % yesterday.isoformat()[:10],
    "HTMLContent": content,
})
# print(response.text)
# import sys; sys.exit(0)

assert response.status_code == 200
json = response.json()
assert json["Success"], json["ErrorMessage"]
campaign_id = json["CampaignID"]

response = requests.post(config.SENDLOOP_BASE_URL + "/Campaign.Send/json", data={
    "APIKey": config.SENDLOOP_API_KEY,
    "CampaignID": campaign_id,
    "SendDate": "NOW",
})
assert response.status_code == 200
json = response.json()
assert json["Success"], json["ErrorMessage"]
