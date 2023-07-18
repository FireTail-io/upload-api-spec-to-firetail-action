import importlib
import json
import os
import sys
import responses
import pytest
import unittest
from freezegun import freeze_time

sys.path.insert(1, "./src/")

# Global variables to store the request data
request_body = None
request_headers = None


def load_json_file(location):
    f = open(location, "r")
    data = json.loads(f.read())
    f.close()
    return data


class FoundationalFunctions:
    def verify_request_made_correctly(self, request_index=0):
        """
        Verifies that the request was made correctly.

        Args:
            request_index: The index of the request in the responses.calls list. Defaults to 0.
        """
        request = responses.calls[request_index].request
        assert request.url == f"{self.app_spec_module.FIRETAIL_API_URL}/code_repository/spec"
        assert request.method == "POST"
        assert request.headers["x-ft-api-key"] == "mock-token"

    def mock_response(self, status, json_data=None, callback=None):
        """
        Mocks the response from the Firetail API.

        Args:
            status: The status code to return in the response.
            json_data: The JSON data to return in the response. Defaults to None.
            callback: The callback function to call when a request is made to the mocked API endpoint. Defaults to None.
        """
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


class TestProcessAPISpec(FoundationalFunctions):
    app_spec_module = import_app_spec_module()

    def setup_method(self, method):
        """
        Resets the responses object and sets the app_spec_module variables to their default values.

        Args:
            method: The method being run.
        """
        responses.reset()
        self.app_spec_module.API_SPEC_LOCATION = "tests/openapi/good_3.1_spec.yaml"
        self.app_spec_module.FIRETAIL_API_URL = "https://mock-url.com/api"
        self.app_spec_module.FIRETAIL_API_TOKEN = "mock-token"
        self.app_spec_module.COLLECTION_UUID = "mock-uuid"
        global request_body
        global request_headers
        request_body = None
        request_headers = None

    @responses.activate
    def test_api_post_successfully(self):
        """
        Test that the API is called correctly when the API spec is successfully uploaded.
        """
        self.mock_response(201, callback=request_callback)

        self.app_spec_module.send_spec_to_firetail()

        self.verify_request_made_correctly()

        # Check that the request body was correct
        request_data = json.loads(request_body)
        assert request_data["collection_uuid"] == "mock-uuid"

    @responses.activate
    def test_api_internal_server_error(self):
        """
        Test that an exception is raised when the API returns a 500 error.
        """
        self.mock_response(500, json_data={"error": "Internal server error"})

        with pytest.raises(Exception) as e:
            self.app_spec_module.send_spec_to_firetail()
        assert str(e.value) == 'Failed to send FireTail API Spec. {"error": "Internal server error"}'

        self.verify_request_made_correctly()

    @responses.activate
    def test_api_bad_request(self):
        """
        Test that an exception is raised when the API returns a 400 error.
        """
        self.mock_response(400, json_data={"error": "Bad request"})

        with pytest.raises(Exception) as e:
            self.app_spec_module.send_spec_to_firetail()
        assert str(e.value) == 'Failed to send FireTail API Spec. {"error": "Bad request"}'

        self.verify_request_made_correctly()

    @responses.activate
    def test_missing_api_key(self):
        """
        Test that an exception is raised when the API key is missing.
        """
        with unittest.mock.patch.object(self.app_spec_module, "FIRETAIL_API_TOKEN", new=None):
            with pytest.raises(Exception) as e:
                self.app_spec_module.send_spec_to_firetail()
            assert str(e.value) == "Missing FireTail API token"

    @responses.activate
    def test_missing_collection_uuid(self):
        """
        Test that an exception is raised when the collection UUID is missing.
        """
        self.app_spec_module.COLLECTION_UUID = None

        with pytest.raises(Exception) as e:
            self.app_spec_module.send_spec_to_firetail()
        assert str(e.value) == "Missing FireTail API collection UUID"

    @responses.activate
    def test_missing_spec_file(self):
        """
        Test that an exception is raised when the API spec file is missing.
        """
        self.app_spec_module.API_SPEC_LOCATION = "fake_file.yaml"

        with pytest.raises(Exception) as e:
            self.app_spec_module.send_spec_to_firetail()
        assert str(e.value) == "API Spec file could not be found at fake_file.yaml"

    @responses.activate
    def test_invalid_spec_file(self):
        """
        Test that an exception is raised when the API spec file is invalid.
        """
        self.app_spec_module.API_SPEC_LOCATION = "tests/openapi/bad_3.1_spec.yaml"

        with pytest.raises(Exception) as e:
            self.app_spec_module.send_spec_to_firetail()
        assert str(e.value) == "Failed to parse YAML. Spec is invalid."

    @responses.activate
    def test_multiple_api_calls(self):
        """
        Test that multiple API calls are made when the API spec is sent to Firetail multiple times.
        """
        self.mock_response(201, callback=request_callback)

        for _ in range(5):
            self.app_spec_module.send_spec_to_firetail()

        assert len(responses.calls) == 5

        for i in range(5):
            self.verify_request_made_correctly(i)


class TestContext(FoundationalFunctions):
    app_spec_module = import_app_spec_module()

    def setup_method(self, method):
        """
        Resets the responses object and sets the app_spec_module variables to their default values.

        Args:
            method: The method being run.
        """
        responses.reset()
        context_file = load_json_file("tests/example/github_context.json")
        self.app_spec_module.CONTEXT = context_file
        self.app_spec_module.API_SPEC_LOCATION = "tests/openapi/good_3.1_spec.yaml"
        self.app_spec_module.FIRETAIL_API_URL = "https://mock-url.com/api"
        self.app_spec_module.FIRETAIL_API_TOKEN = "mock-token"
        self.app_spec_module.COLLECTION_UUID = "mock-uuid"
        global request_body
        global request_headers
        request_body = None
        request_headers = None

    @responses.activate
    @freeze_time("2012-01-14")
    def test_context_passed(self):
        """
        Test context was passed in correctly
        """
        self.mock_response(201, callback=request_callback)

        self.app_spec_module.send_spec_to_firetail()

        self.verify_request_made_correctly()

        # Check that the request body was correct
        request_data = json.loads(request_body)
        assert request_data["context"] == {
            "sha": "d4320sse72c629c804e189cf591f3fe091941345",
            "repository": "company/test-repo",
            "ref": "refs/heads/dev",
            "head_commit_username": "exampleuser",
            "actor": "exampleuser",
            "workflow_ref": "company/test-repo/.github/workflows/test_action.yaml@refs/heads/dev",
            "event_name": "push",
            "private": True,
            "run_id": "5589140733",
            "time_triggered": 1326499200000000,
        }
