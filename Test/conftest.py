
import os
import json
import pytest
# from test_helpers import request_wiz_api_token, discover_policies
import test_helpers


# The conftest.py file is used to define fixtures and command-line options that can be used across multiple test files.
# In this case, the conftest.py file defines a fixture named auth_token that requests an API token from the Wiz API.
# The fixture is used in the test_metadata.py and test_policies.py test files to authenticate with the Wiz API.
# The conftest.py file also defines a fixture named get_schema that loads the metadata schema from a JSON file.
# The get_schema fixture is used in the test_metadata.py test file to validate policy metadata against the schema.
# The conftest.py file defines a command-line option named --control_id that can be used to specify the ID of a control to run tests for.
# The --control_id option is used in the pytest_generate_tests function to filter policies based on the control ID.
# The pytest_generate_tests function generates test cases based on the policies that match the specified control ID.
# The test_policy function in test_policies.py runs tests based on metadata and API responses for each policy.
# The test_metadata_validate function in test_metadata.py validates policy metadata against a schema for each policy.
# The test_pass_fail_case_added function in test_metadata.py checks if each policy has at least one pass and fail test case.
# Overall, the conftest.py file provides reusable fixtures and options for testing policies and metadata in the Wiz platform.


# find script directory
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
print(f"SCRIPT_DIR : {SCRIPT_DIR}")
# check if the base directory's last folder is Test
if os.path.basename(SCRIPT_DIR) == "Test":
    # if it is, then go up one level
    ROOT_DIR = os.path.dirname(SCRIPT_DIR)
else:
    ROOT_DIR = SCRIPT_DIR

POLICY_DIR = os.path.join(ROOT_DIR, "DigitalPolicies")
print(f"POLICY_DIR : {POLICY_DIR}")

@pytest.fixture(scope="session")
def auth_token():
    '''Request an API token from the Wiz API.'''
    token, dc = test_helpers.request_wiz_api_token()
    return token, dc

@pytest.fixture()
def get_schema(request):
    '''Load the metadata schema from a JSON file.'''
    test_dir = os.path.dirname(request.module.__file__)
    data_filename = os.path.join(test_dir, "metadata-schema.json")
    with open(data_filename, "r", encoding="utf-8") as f:
        return json.load(f)

def pytest_addoption(parser):
    '''Add a command-line option to specify the ID of a control to run tests for.'''
    parser.addoption("--control_id", action="store", default = None, help="ID of the control to run tests for")

def pytest_generate_tests(metafunc):
    '''Generate test cases based on the policies that match the specified control ID.'''
    # check if os.environ.get('CI_COMMIT_REF_NAME') is set
    control_id = metafunc.config.getoption("control_id") or test_helpers.get_control_id_from_current_branch() or "all"
    print(control_id)
    all_terraform_policies = test_helpers.discover_policies(POLICY_DIR, control_id)
    all_cloud_policies = test_helpers.discover_cloud_matcher_policies(POLICY_DIR, control_id)
    print(f"Total policies with terraform matcher enabled : {len(all_terraform_policies)}")
    print(f"Total policies with cloud matcher enabled : {len(all_cloud_policies)}")
    # Collect all test cases from all policies
    if 'metadata_validate_path' in metafunc.fixturenames:
        test_ids = [f"{policy['folder_name']}" for policy in all_terraform_policies]
        metafunc.parametrize("metadata_validate_path", all_terraform_policies, ids=test_ids)
    elif 'test_terraform' in metafunc.fixturenames:
        all_test_cases = []
        for policy in all_terraform_policies:
            all_test_cases.extend(test_helpers.collect_terraform_test_cases(policy,POLICY_DIR))
        test_ids = [f"{case['ccr_dir_name']}/terraform/tests/{case['filename']}::{case['description']}" for case in all_test_cases]
        metafunc.parametrize("test_terraform", all_test_cases, ids=test_ids)
    elif 'test_cloud' in metafunc.fixturenames:
        all_test_cases = []
        for policy in all_cloud_policies:
            all_test_cases.extend(test_helpers.collect_cloud_test_cases(policy,POLICY_DIR))
        test_ids = [f"{case['ccr_dir_name']}/cloud/tests/{case['filename']}::{case['description']}" for case in all_test_cases]
        metafunc.parametrize("test_cloud", all_test_cases, ids=test_ids)
    elif 'terraform_matcher_pass_case' in metafunc.fixturenames:
        test_ids = [f"{policy['folder_name']}" for policy in all_terraform_policies ]
        metafunc.parametrize("terraform_matcher_pass_case", all_terraform_policies, ids=test_ids)
    elif 'cloud_matcher_pass_case' in metafunc.fixturenames:
        test_ids = [f"{policy['folder_name']}" for policy in all_cloud_policies]
        metafunc.parametrize("cloud_matcher_pass_case", all_cloud_policies, ids=test_ids)
