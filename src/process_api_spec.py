# src/get_num_square.py
import os
import requests
import json
import yaml 


# get the input and convert it to int
FIRETAIL_API_URL = os.environ.get("FIRETAIL_API_URL", "https://api.saas.eu-west-1.prod.firetail.app")
FIRETAIL_API_TOKEN = os.environ.get("FIRETAIL_API_TOKEN")
COLLECTION_UUID = os.environ.get("COLLECTION_UUID")
API_SPEC_LOCATION = os.environ.get("API_SPEC_LOCATION")


def load_from_fs():
    if not os.path.exists(API_SPEC_LOCATION):
        raise Exception(f"API Spec file could not be found at {API_SPEC_LOCATION}")
    with open(API_SPEC_LOCATION, 'r') as file_handler:
        if API_SPEC_LOCATION.lower().endswith(("yaml", "yml")):
            # load yaml
            spec = yaml.safe_load(file_handler)
        if API_SPEC_LOCATION.lower().endswith("json"):
            # load json
            spec = json.loads(file_handler.read())
    return spec
    

def send_spec_to_firetail():
    spec_data = load_from_fs()
    json_data = {
        "collection_uuid": COLLECTION_UUID,
        "spec_file": spec_data
    }
    response = requests.post(url=f"{FIRETAIL_API_URL}/code_repository/spec", json=json_data)
    if response.status_code != 201:
        raise Exception("Failed to send FireTail API Spec")
