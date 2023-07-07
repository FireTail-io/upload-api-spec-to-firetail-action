# src/get_num_square.py
import os
import requests
import json
import yaml
from prance import ResolvingParser
from prance.util.resolver import RESOLVE_INTERNAL

FIRETAIL_API_URL = os.environ.get("FIRETAIL_API_URL", "https://api.saas.eu-west-1.prod.firetail.app")
FIRETAIL_API_TOKEN = os.environ.get("FIRETAIL_API_TOKEN")
COLLECTION_UUID = os.environ.get("COLLECTION_UUID")
API_SPEC_LOCATION = os.environ.get("API_SPEC_LOCATION")


class SpecDataValidationError(Exception):
    pass


def load_from_fs():
    if not API_SPEC_LOCATION:
        raise Exception("API_SPEC_LOCATION not defined")
    if not os.path.exists(API_SPEC_LOCATION):
        raise Exception(f"API Spec file could not be found at {API_SPEC_LOCATION}")
    with open(API_SPEC_LOCATION, "r") as file_handler:
        try:
            if API_SPEC_LOCATION.lower().endswith(("yaml", "yml")):
                # load yaml
                spec = yaml.safe_load(file_handler)
            elif API_SPEC_LOCATION.lower().endswith("json"):
                # load json
                spec = json.loads(file_handler.read())
            else:
                raise ValueError(f"Unknown file type for API Spec: {API_SPEC_LOCATION}")
        except yaml.YAMLError:
            raise Exception(f"Failed to parse YAML. Spec is invalid.")
        except json.JSONDecodeError:
            raise Exception(f"Failed to parse JSON")
        except Exception:
            raise Exception(f"Failed to read API spec file. Spec is invalid.")
    return spec


def is_spec_valid(spec_data: dict) -> bool:
    parser = ResolvingParser(
        spec_string=json.dumps(spec_data, default=str),
        resolve_types=RESOLVE_INTERNAL,
        backend="openapi-spec-validator",
        lazy=True,
    )
    try:
        parser.parse()
    except Exception:
        # In the future, maybe we can provide some proper details here.
        return False
    return True


def check_environment_variables():
    if not FIRETAIL_API_TOKEN:
        raise Exception("Missing FireTail API token")
    if not COLLECTION_UUID:
        raise Exception("Missing FireTail API collection UUID")
    if not FIRETAIL_API_URL:
        raise Exception("Missing FireTail API URL")


def resolve_and_validate_spec_data(spec_data: dict) -> dict:
    if not is_spec_valid(spec_data):
        raise SpecDataValidationError()

    return spec_data


def get_spec_type(spec_data: dict):
    if spec_data.get("openapi").startswith("3.1"):
        return "OAS3.1"
    if spec_data.get("swagger"):
        return "SWAGGER2"

    return "OAS3.0"


def send_spec_to_firetail():
    check_environment_variables()
    spec_data = load_from_fs()

    try:
        spec_data = resolve_and_validate_spec_data(spec_data)
    except SpecDataValidationError:
        return Exception("Spec file is not valid")

    json_data = {"collection_uuid": COLLECTION_UUID, "spec_data": spec_data, "spec_type": get_spec_type(spec_data)}
    response = requests.post(
        url=f"{FIRETAIL_API_URL}/code_repository/spec", json=json_data, headers={"x-ft-api-key": FIRETAIL_API_TOKEN}
    )
    if response.status_code not in {201, 409}:
        raise Exception(f"Failed to send FireTail API Spec. {response.text}")


if __name__ == "__main__":
    send_spec_to_firetail()
