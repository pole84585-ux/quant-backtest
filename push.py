import requests
import os

def push(msg):

    key = os.getenv("PUSHDEER_KEY")

    url = f"https://api2.pushdeer.com/message/push?pushkey={key}&text={msg}"

    requests.get(url)
