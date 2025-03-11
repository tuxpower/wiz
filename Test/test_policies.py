import os
import pytest
import json
from jsonschema import validate
from git import Repo
import test_helpers
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class RateLimitExceededError(Exception):
    pass

@retry(
    stop=stop_after_attempt(5),  # Retry up to 5 times
    wait=wait_exponential(multiplier=1, min=4, max=60),  # Exponential backoff: 4-60 seconds
    retry=retry_if_exception_type(RateLimitExceededError)  # Retry only on RateLimitExceededError
)
def query_wiz_api_with_retry(query, variables, dc, token):
    """Call the API with retry logic applied."""
    # Call the API with the provided query, variables, data center, and token
    result = test_helpers.query_wiz_api(query, variables, dc, token)
    # Check if the result contains any errors
    if result.get("errors"):
        # If any error message contains "Rate limit exceeded", raise a custom exception
        if any("Rate limit exceeded" in error.get("message", "") for error in result['errors']):
            raise RateLimitExceededError("Rate limit exceeded")

    # Return the result from the API call
    return result


def test_terraform_matcher(test_terraform, auth_token):
    """Run tests based on metadata."""

    # Construct the path to the input file
    input_file = os.path.join(test_terraform['test_path'], test_terraform['filename'])

    # Get the rego file path
    rego_file = test_terraform['rego_path']
    # Extract the token and data center from the auth_token
    token, dc = auth_token

    # Get the payload for the API call
    variables, query = test_helpers.get_payload_for_terraform_matcher(input_file, rego_file, test_terraform['iac_type'], dc, token)
    # print(json.dumps(variables, indent=4))
    # print(json.dumps(query, indent=4))

    result_status = None

    # Call the API with retry logic applied
    result = query_wiz_api_with_retry(query, variables, dc, token)
    # print(json.dumps(result, indent=4))
    # Check if the result contains data
    if result.get('data'):
        # Extract the result status from the API response
        result_status = result['data']["cloudConfigurationRuleIaCTest"]['result']
    elif result.get("errors"):
        # If there are errors, print the first error message
        if len(result['errors']) > 0:
            print(result['errors'][0]['message'])
        result_status = "FAILED"

    # Assert that the policy correctly identifies the violation
    assert result_status == test_terraform['expected_result'], f"Policy did not produce expected result for {input_file}"


def test_cloud_matcher(test_cloud, auth_token):
    """Run tests based on metadata."""

    # Construct the path to the input file
    input_file = os.path.join(test_cloud['test_path'], test_cloud['filename'])

    # Get the rego file path
    rego_file = test_cloud['rego_path']
    # Extract the token and data center from the auth_token
    token, dc = auth_token

    # Get the payload for the API call
    variables, query = test_helpers.get_payload_for_cloud_matcher(input_file, rego_file)
    # print(json.dumps(variables, indent=4))

    result_status = None

    # Call the API with retry logic applied
    result = query_wiz_api_with_retry(query, variables, dc, token)
    # Check if the result contains data
    if result.get('data'):
        # Extract the result status from the API response
        result_status = result['data']["cloudConfigurationRuleJsonTest"]['result']
    elif result.get("errors"):
        # If there are errors, print the first error message
        if len(result['errors']) > 0:
            print(result['errors'][0]['message'])
        result_status = "FAILED"

    # Assert that the policy correctly identifies the violation
    assert result_status == test_cloud['expected_result'], f"Policy did not produce expected result for {input_file}"
