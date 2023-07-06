import importlib
import json
import os
import sys
import responses
import pytest

sys.path.insert(1, "./src/")

# Global variables to store the request data
request_body = None
request_headers = None


def request_callback(request):
    """
    Callback function for the requests library. This function will be called when a request is made to the Firetail API.

    Args:
        request (requests.Request): An object representing the HTTP request made to the mocked API endpoint.

    Returns:
        tuple: A tuple containing the HTTP status code, headers, and body of the response.
    """
    global request_headers
    global request_body

    request_headers = request.headers
    request_body = request.body

    headers = {}
    response_body = {"status": "success"}

    return (201, headers, json.dumps(response_body))


def import_app_spec_module():
    """
    Imports the app_spec_module module from the src directory. This is done to avoid having to install the package

    Returns:
        module: The app_spec_module module
    """
    if "process_api_spec" in sys.modules:
        del sys.modules["process_api_spec"]
    return importlib.import_module("process_api_spec")


class TestProcessAPISpec:
    app_spec_module = import_app_spec_module()

    def setup_method(self, method):
        self.app_spec_module.API_SPEC_LOCATION = "tests/openapi/good_3.1_spec.yaml"
        self.app_spec_module.FIRETAIL_API_URL = "https://mock-url.com/api"
        self.app_spec_module.FIRETAIL_API_TOKEN = "mock-token"
        self.app_spec_module.COLLECTION_UUID = "mock-uuid"
        global request_body
        global request_headers
        request_body = None
        request_headers = None

    def mock_response(self, status, json_data=None, callback=None):
        if callback is None:
            responses.add(
                responses.POST,
                f"{self.app_spec_module.FIRETAIL_API_URL}/code_repository/spec",
                json=json_data,
                status=status,
            )
        else:
            responses.add_callback(
                responses.POST,
                f"{self.app_spec_module.FIRETAIL_API_URL}/code_repository/spec",
                callback=callback,
            )

    def verify_request_made_correctly(self):
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.url == f"{self.app_spec_module.FIRETAIL_API_URL}/code_repository/spec"
        assert request.method == "POST"
        assert request.headers["x-ft-api-key"] == "mock-token"

    @responses.activate
    def test_api_post_successfully(self):
        self.mock_response(201, callback=request_callback)

        self.app_spec_module.send_spec_to_firetail()

        self.verify_request_made_correctly()

        # Check that the request body was correct
        request_data = json.loads(request_body)
        assert request_data["collection_uuid"] == "mock-uuid"

    @responses.activate
    def test_api_internal_server_error(self):
        self.mock_response(500, json_data={"error": "Internal server error"})

        with pytest.raises(Exception) as e:
            self.app_spec_module.send_spec_to_firetail()
        assert str(e.value) == 'Failed to send FireTail API Spec. {"error": "Internal server error"}'

        self.verify_request_made_correctly()

    @responses.activate
    def test_api_bad_request(self):
        self.mock_response(400, json_data={"error": "Bad request"})

        with pytest.raises(Exception) as e:
            self.app_spec_module.send_spec_to_firetail()
        assert str(e.value) == 'Failed to send FireTail API Spec. {"error": "Bad request"}'

        self.verify_request_made_correctly()

    @responses.activate
    def test_missing_api_key(self):
        self.app_spec_module.FIRETAIL_API_TOKEN = None

        with pytest.raises(Exception) as e:
            self.app_spec_module.send_spec_to_firetail()
        assert str(e.value) == "Missing FireTail API token"
