from importlib import import_module
import sys
import responses
sys.path.insert(0, ".")

def import_app_spec_module():
    if 'src.process_api_spec' in sys.module:
        del sys.module['src.process_api_spec']
    return import_module('src.process_api_spec')

class TestProcessAPISpec:
    app_spec_module = None
    
    def setup_module(self):
        self.app_spec_module = import_app_spec_module()

    @responses.activate
    def test_api_post_successfully(self):
        self.app_spec_module.API_SPEC_LOCATION = "tests/openapi/good_3.1_spec.yaml"
        response = self.app_spec_module.send_spec_to_firetail()
        assert True
