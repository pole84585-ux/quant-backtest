import requests
import config

def push(msg):
    requests.post(
        "https://api2.pushdeer.com/message/push",
        data={
            "pushkey": config.PUSHDEER_KEY,
            "text": msg
        }
    )
