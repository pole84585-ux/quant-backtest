import json

FILE = "state.json"

def load():
    try:
        return json.load(open(FILE))
    except:
        return {"history": []}

def save(data):
    json.dump(data, open(FILE, "w"))
