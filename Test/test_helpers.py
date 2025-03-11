import os
import base64
import json
import requests
from git import Repo

HEADERS_AUTH = {"Content-Type": "application/x-www-form-urlencoded"}

class CredentialsNotProvidedException(Exception):
    pass

def request_wiz_api_token():
    """Retrieve an OAuth access token to be used against Wiz API"""
    CLIENT_ID = os.environ.get("WIZ_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("WIZ_CLIENT_SECRET")

    if CLIENT_ID is None:
        raise CredentialsNotProvidedException("Please set environment variable 'WIZ_CLIENT_ID'")
    if CLIENT_SECRET is None:
        raise CredentialsNotProvidedException("Please set environment variable 'WIZ_CLIENT_SECRET'")

    auth_payload = {
      'grant_type': 'client_credentials',
      'audience': 'wiz-api',
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET
    }
    try:
        # Uncomment the next first line and comment the line after that
        # to run behind proxies
        # response = requests.post(url="https://auth.app.wiz.io/oauth/token",
        #                         headers=HEADERS_AUTH, data=auth_payload,
        #                         proxies=proxyDict, timeout=180)
        response = requests.post(url="https://auth.app.wiz.io/oauth/token",
                                headers=HEADERS_AUTH, data=auth_payload, timeout=180)

    except requests.exceptions.HTTPError as e:
        print(f"<p>Error authenticating to Wiz (4xx/5xx): {str(e)}</p>")
        return e

    except requests.exceptions.ConnectionError as e:
        print(f"<p>Network problem (DNS failure, refused connection, etc): {str(e)}</p>")
        return e

    except requests.exceptions.Timeout as e:
        print(f"<p>Request timed out: {str(e)}</p>")
        return e

    try:
        response_json = response.json()
        token = response_json.get('access_token')
        if not token:
            message = f"Could not retrieve token from Wiz: {response_json.get('message')}"
            raise ValueError(message)
    except ValueError as exception:
        message = f"Could not parse API response {exception}. Check Service Account details " \
                    "and variables"
        raise ValueError(message) from exception

    response_json_decoded = json.loads(
        base64.standard_b64decode(pad_base64(token.split(".")[1]))
    )

    response_json_decoded = json.loads(
        base64.standard_b64decode(pad_base64(token.split(".")[1]))
    )
    dc = response_json_decoded["dc"]

    return token, dc


def pad_base64(data):
    """Makes sure base64 data is padded"""
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += "=" * (4 - missing_padding)
    return data



def query_wiz_api(query, variables, dc, token):
    """Query Wiz API for the given query data schema"""
    headers = {"Content-Type": "application/json"}

    headers["Authorization"] = "Bearer " + token
    data = {"variables": variables, "query": query}

    try:
        # Uncomment the next first line and comment the line after that
        # to run behind proxies
        # result = requests.post(url=f"https://api.{dc}.app.wiz.io/graphql",
        #                        json=data, headers=HEADERS, proxies=proxyDict, timeout=180)
        result = requests.post(url=f"https://api.{dc}.app.wiz.io/graphql",
                               json=data, headers=headers, timeout=180)

    except requests.exceptions.HTTPError as e:
        print(f"<p>Wiz-API-Error (4xx/5xx): {str(e)}</p>")
        return e

    except requests.exceptions.ConnectionError as e:
        print(f"<p>Network problem (DNS failure, refused connection, etc): {str(e)}</p>")
        return e

    except requests.exceptions.Timeout as e:
        print(f"<p>Request timed out: {str(e)}</p>")
        return e

    return result.json()

def get_payload_for_cloud_matcher(json_file,policy_file):
    """The GraphQL query that defines which data you wish to fetch."""
    query = """
        query RunCloudRegoRuleTestWithJson($rule: String!, $json: JSON!) {
            cloudConfigurationRuleJsonTest(rule: $rule, json: $json) {
                result
                output
                evidence {
                current
                expected
                path
                }
            }
        }
    """

    # Open the proposed Rego file
    with open(policy_file, 'r',encoding="utf-8") as rego_file:
        rego_file_contents = rego_file.read()

    json_file_contents = load_json(json_file)
    # The variables sent along with the above query
    variables = {
        "json": json_file_contents,
        "rule": rego_file_contents
    }


    return variables, query


def get_payload_for_terraform_matcher(iac_file,policy_file, iac_type, dc, token):
    """The GraphQL query that defines which data you wish to fetch."""
    query = """
        query RunIaCTestWithFile($rule: String!, $IaCFileContent: String!, $type: CloudConfigurationRuleMatcherType!) {
        cloudConfigurationRuleIaCTest(
            rule: $rule
            IaCFileContent: $IaCFileContent
            type: $type
        ) {
            result
            output
            evidence {
            current
            expected
            path
            }
        }
        }
    """
    if iac_file.endswith(".json"):
        variables, json_query = get_json_input_for_terraform_matcher(iac_file, iac_type)
        # Call the API
        result = query_wiz_api(json_query, variables, dc, token)
        iac_file_contents = json.dumps(result['data']['convertIaCFileToResourceJson']['resourceJSONs'][0], indent=4)

        # iac_file_contents = json.dumps(result)
    else:
        # Open the sample IaC file to evaluate against the proposed Rego Code
        with open(iac_file, 'r',encoding="utf-8") as input_file:
            iac_file_contents = input_file.read()

    # Open the proposed Rego file
    with open(policy_file, 'r',encoding="utf-8") as rego_file:
        rego_file_contents = rego_file.read()

    # The variables sent along with the above query
    variables = {
        "IaCFileContent": iac_file_contents,
        "rule": rego_file_contents,
        "type": iac_type.upper()
    }

    return variables, query

def get_json_input_for_terraform_matcher(iac_file,iac_type):

    """The GraphQL query that defines which data you wish to fetch."""
    query = """
    query ConvertIaCFileToJSON($IaCFileContent: String!, $type: CloudConfigurationRuleMatcherType!) {
      convertIaCFileToResourceJson(IaCFileContent: $IaCFileContent, type: $type) {
        resourceJSONs
      }
    }
    """
     # Open the sample IaC file to evaluate against the proposed Rego Code
    with open(iac_file, 'r',encoding="utf-8") as input_file:
        iac_file_contents = input_file.read()

    # The variables sent along with the above query
    variables = {
        "IaCFileContent": iac_file_contents,
        "type": iac_type.upper()
    }
    # print(variables)
    return variables, query

def load_test_metadata(metadata_file):
    """Load the test metadata from the JSON file."""
    with open(metadata_file,'r',encoding="utf-8") as f:
        return json.load(f)

def load_json(json_file):
    """Load the test metadata from the JSON file."""
    with open(json_file,'r',encoding="utf-8") as f:
        return json.load(f)

def discover_policies(base_dir, control_id=None):
    """Discover all policy directories"""

    policies = []
    # print(f"Discovering policies in {base_dir} {control_id}")
    # check if base_dir exists
    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} does not exist")
        return policies
    for item in os.listdir(base_dir):

        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            folder_name_only = os.path.basename(item_path)
            if control_id == "all" :
                policies.append({
                    "folder_name": folder_name_only,
                    "folder_path": item_path
                })
            else:
                if folder_name_only.startswith(control_id):
                    policies.append({
                        "folder_name": folder_name_only,
                        "folder_path": item_path
                    })
                    continue

    # sort the policies by folder name
    policies = sorted(policies, key=lambda k: k['folder_name'])
    enabled_policies = []
    # get policies that are enabled
    for policy in policies:
        metadata_path = os.path.join(base_dir, policy['folder_name'], 'metadata', 'metadata.json')
        metadata = load_test_metadata(metadata_path)
        if metadata['enabled']:
            enabled_policies.append(policy)

    return enabled_policies

def discover_cloud_matcher_policies(base_dir, control_id=None):
    """Discover all policy directories"""

    policies = []
    # print(f"Discovering policies in {base_dir} {control_id}")
    # check if base_dir exists
    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} does not exist")
        return policies
    for item in os.listdir(base_dir):

        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            folder_name_only = os.path.basename(item_path)
            cloud_folder = os.path.join(item_path, 'cloud')
            if not os.path.exists(cloud_folder):
                continue

            if control_id == "all" :
                policies.append({
                    "folder_name": folder_name_only,
                    "folder_path": item_path
                })
            else:
                if folder_name_only.startswith(control_id):
                    policies.append({
                        "folder_name": folder_name_only,
                        "folder_path": item_path
                    })
                    continue

    # sort the policies by folder name
    policies = sorted(policies, key=lambda k: k['folder_name'])
    enabled_policies = []
    # get policies that are enabled
    for policy in policies:
        metadata_path = os.path.join(base_dir, policy['folder_name'], 'metadata', 'metadata.json')
        metadata = load_test_metadata(metadata_path)
        if metadata['enabled']:
            enabled_policies.append(policy)

    return enabled_policies


def get_control_id_from_current_branch():
    """
    Get the current branch name of the Git repository.

    :param repo_path: Path to the Git repository.
    :return: Current branch name.
    """
    # check if the environment variable contains key CI_COMMIT_REF_NAME, get the value from it
    ci_commit_ref_name = os.environ.get('CI_COMMIT_REF_NAME')
    if ci_commit_ref_name:
        current_branch = ci_commit_ref_name
    else:
        repo_path = os.path.dirname(os.path.abspath(__file__))
        repo_path = repo_path.replace("Test", "")
        repo = Repo(repo_path)
        current_branch = repo.active_branch.name


    # Check if the current_branch has 'hotfix' or 'feature' in it then retrieve the text after 'hotfix/'
    if 'hotfix/' in current_branch:
        control_id = current_branch.split('hotfix/', 1)[1]
        print(f"Hotfix branch detected: {current_branch}, only tests belongs to the control_id: {control_id} will be executed")
    elif 'feature/' in current_branch:
        control_id = current_branch.split('feature/', 1)[1]
        print(f"Feature branch detected: {current_branch}, only tests belongs to the control_id: {control_id} will be executed ")
    elif 'develop' in current_branch or "main" in current_branch:
        control_id = "all"
    else:
        control_id = None

    return control_id


def collect_terraform_test_cases(ccr_dir_det, base_dir):
    """Collect test cases from the policy directory for terraform matcher."""
    # Construct the path to the policy file
    ccr_dir = ccr_dir_det['folder_path']
    rego_path = os.path.join(base_dir, ccr_dir, "terraform", "query.rego")

    # Construct the path to the test metadata file
    test_metadata_path = os.path.join(base_dir, ccr_dir, 'terraform', 'tests', 'test-metadata.json')

    # Load the test metadata from the JSON file
    test_metadata = load_test_metadata(test_metadata_path)

    # Construct the path to the test cases directory
    test_path = os.path.join(base_dir, ccr_dir, 'terraform','tests')

    # Select the test cases which are enabled (enabled == true)
    enabled_test_metadata = [case for case in test_metadata if case['enabled']]
    # check if any ignore test cases are present, then skip them
    valid_test_metadata = []
    ignored_count = 0
    for case in enabled_test_metadata:
        ignore = case.get('ignore',False)
        if ignore:
            ignored_count += 1
            continue
        valid_test_metadata.append(case)
    if ignored_count >0:
        print(f"Total tests ignored: {ignored_count}")
    # get the folder name from the policy_dir
    ccr_dir_name = ccr_dir_det['folder_name']
    # Include policy directory in the test case for identification
    for case in valid_test_metadata:
        case['ccr_dir'] = ccr_dir
        case['ccr_dir_name'] = ccr_dir_name
        case['rego_path'] = rego_path
        case['test_path'] = test_path
        # case['iac_type'] = policy_dir.split("/")[-1]
        case['iac_type'] = "terraform"

    return valid_test_metadata


def collect_cloud_test_cases(ccr_dir_det, base_dir):
    """Collect test cases from the policy directory for cloud matcher."""
    # Construct the path to the policy file
    ccr_dir = ccr_dir_det['folder_path']
    rego_path = os.path.join(base_dir, ccr_dir, "cloud", "query.rego")

    # Construct the path to the test metadata file
    test_metadata_path = os.path.join(base_dir, ccr_dir, 'cloud', 'tests', 'test-metadata.json')

    # check test_metadata_path exists
    if not os.path.exists(test_metadata_path):
        print(f"Test metadata file {test_metadata_path} does not exist")
        return []
    # Load the test metadata from the JSON file
    test_metadata = load_test_metadata(test_metadata_path)

    # Construct the path to the test cases directory
    test_path = os.path.join(base_dir, ccr_dir, 'cloud','tests')

    # Select the test cases which are enabled (enabled == true)
    enabled_test_metadata = [case for case in test_metadata if case['enabled']]
    # check if any ignore test cases are present, then skip them
    valid_test_metadata = []
    ignored_count = 0
    for case in enabled_test_metadata:
        ignore = case.get('ignore',False)
        if ignore:
            ignored_count += 1
            continue
        valid_test_metadata.append(case)
    if ignored_count >0:
        print(f"Total tests ignored: {ignored_count}")
    # get the folder name from the policy_dir
    ccr_dir_name = ccr_dir_det['folder_name']
    # Include policy directory in the test case for identification
    for case in valid_test_metadata:
        case['ccr_dir'] = ccr_dir
        case['ccr_dir_name'] = ccr_dir_name
        case['rego_path'] = rego_path
        case['test_path'] = test_path


    return valid_test_metadata
