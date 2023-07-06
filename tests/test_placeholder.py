import importlib
import os
import sys
import responses

sys.path.insert(1, "./src/")


def import_app_spec_module():
    if "process_api_spec" in sys.modules:
        del sys.modules["process_api_spec"]
    return importlib.import_module("process_api_spec")


class TestProcessAPISpec:
    app_spec_module = import_app_spec_module()

    @responses.activate
    def test_api_post_successfully(self):
        # Mock the environment variables
        self.app_spec_module.API_SPEC_LOCATION = "tests/openapi/good_3.1_spec.yaml"
        self.app_spec_module.FIRETAIL_API_URL = "https://mock-url.com/api"
        self.app_spec_module.FIRETAIL_API_TOKEN = "mock-token"
        self.app_spec_module.COLLECTION_UUID = "mock-uuid"

        # Mock the response from Firetail
        responses.add(
            responses.POST,
            f"{self.app_spec_module.FIRETAIL_API_URL}/code_repository/spec",
            json={"status": "success"},
            status=201,
        )

        self.app_spec_module.send_spec_to_firetail()

        # Check that the request was made correctly
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == f"{self.app_spec_module.FIRETAIL_API_URL}/code_repository/spec"
        assert responses.calls[0].request.method == "POST"
        assert responses.calls[0].request.headers["x-ft-api-key"] == "mock-token"
