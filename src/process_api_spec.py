# src/get_num_square.py
import os
import requests
import json
import yaml
from prance import ResolvingParser
from prance.util.resolver import RESOLVE_INTERNAL

from exceptions import SpecDataValidationError

FIRETAIL_API_URL = os.environ.get("FIRETAIL_API_URL", "https://api.saas.eu-west-1.prod.firetail.app")
FIRETAIL_API_TOKEN = os.environ.get("FIRETAIL_API_TOKEN")
COLLECTION_UUID = os.environ.get("COLLECTION_UUID")
API_SPEC_LOCATION = os.environ.get("API_SPEC_LOCATION")


class SpecDataValidationError(Exception):
    pass


def load_from_fs():
    if not os.path.exists(API_SPEC_LOCATION):
        raise Exception(f"API Spec file could not be found at {API_SPEC_LOCATION}")
    with open(API_SPEC_LOCATION, "r") as file_handler:
        if API_SPEC_LOCATION.lower().endswith(("yaml", "yml")):
            # load yaml
            spec = yaml.safe_load(file_handler)
        if API_SPEC_LOCATION.lower().endswith("json"):
            # load json
            spec = json.loads(file_handler.read())
    return spec


def is_spec_valid(spec_data: dict) -> bool:
    parser = ResolvingParser(
        spec_string=json.dumps(spec_data), resolve_types=RESOLVE_INTERNAL, backend="openapi-spec-validator", lazy=True
    )
    try:
        parser.parse()
    except Exception:
        # In the future, maybe we can provide some proper details here.
        return False
    return True


def resolve_and_validate_spec_data(spec_data: dict) -> dict:
    if not is_spec_valid(spec_type, spec_data):
        raise SpecDataValidationError()

    return spec_data


def get_spec_type(spec_data: dict):
    if spec_data.get("openapi").startswith("3.1"):
        return "OAS3.1"
    if spec_data.get("swagger"):
        return "SWAGGER2"

    return "OAS3.0"


def send_spec_to_firetail():
    spec_data = load_from_fs()

    try:
        spec_data = resolve_and_validate_spec_data(spec_data, data["spec_type"])
    except SpecDataValidationError:
        return Exception("Spec file is not valid")

    json_data = {"collection_uuid": COLLECTION_UUID, "spec_file": spec_data, "spec_type": get_spec_type(spec_data)}
    response = requests.post(url=f"{FIRETAIL_API_URL}/code_repository/spec", json=json_data)
    if response.status_code != 201:
        raise Exception("Failed to send FireTail API Spec")
