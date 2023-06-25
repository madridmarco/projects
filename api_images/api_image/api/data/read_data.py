from os import path
import json

with open(path.join('api','data','file_data','credentials.json')) as f:
    credentials = json.load(f)
