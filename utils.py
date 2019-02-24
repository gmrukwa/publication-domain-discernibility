import json
import os


DEFAULT_DESTINATION = os.path.join('data', 'pubs')


def load_json(path: str):
    with open(path) as infile:
        return json.load(infile)


def save_json(path: str, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)
