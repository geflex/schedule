import json


def from_path(path):
    with open(path) as f:
        config = json.load(f)
    return config
