import requests
from flask import Flask, request

import config

app = Flask(__name__, static_folder="")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/kayit", methods=["POST"])
def kayit():
    response = requests.post(config.SENDLOOP_BASE_URL + "/Subscriber.Subscribe/json", data={
        "APIKey": config.SENDLOOP_API_KEY,
        "EmailAddress": request.form["email"],
        "ListID": config.SENDLOOP_LIST_ID,
        "SubscriptionIP": request.remote_addr,
    })
    assert response.status_code == 200

    data = response.json()
    if not data["Success"]:
        if data["ErrorCode"] == 125:
            return "zaten kayitlisiniz."
        raise Exception("Unhandled error code", data["ErrorCode"], data["ErrorMessage"])

    assert data["SubscriptionStatus"] == "Confirmation Pending"
    return "e-posta adresinize bir onay postasi gelecek, " \
           "oradaki linke tiklayin. (gelmediyse spam'a dusmus olabilir)"


if __name__ == "__main__":
    app.run(debug=True)
