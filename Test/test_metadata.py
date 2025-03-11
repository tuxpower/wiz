import os
import pytest
import jsonschema
from jsonschema import validate

import test_helpers

############### validate policy metadata #####################################
def test_metadata_validate(metadata_validate_path, get_schema):
    """
    Test function to validate policy metadata against a given schema.

    This test function uses pytest's parametrize decorator to run the test for each
    policy directory specified in the `all_policies_metadata` list. It constructs
    the path to the metadata file, loads the metadata, and validates it against
    the provided schema.

    Args:
        policy_dir (str): The directory containing the policy metadata.
        get_schema (dict): The schema to validate the metadata against.

    Raises:
        pytest.fail: If the metadata does not conform to the schema, the test fails
        with a message indicating the path of the invalid metadata file.
    """
    # Path to the metadata file
    path = metadata_validate_path['folder_path']
    metadata_path = os.path.join(path, 'metadata','metadata.json')
    metadata = test_helpers.load_json(metadata_path)
    try:
        validate(instance=metadata, schema=get_schema)
    except jsonschema.exceptions.ValidationError as e:
        # General error message
        pytest.fail(f"Validation failed for {metadata_path}. Error: {e.message}. Path: {list(e.path)}. Schema path: {list(e.schema_path)}")

################ check if the policy has atleast one pass and fail test cases #######################################

def get_case(test_metadata, result, test_metadata_path):
    """
    Retrieve a test case from the metadata that matches the expected result.

    Args:
        test_metadata (list): List of test metadata dictionaries.
        result (str): The expected result to filter by (e.g., "PASSED" or "FAILED").

    Returns:
        dict: The test case dictionary that matches the expected result.

    Raises:
        ValueError: If no test case with the expected result is found.
    """
    # Find the first test case that matches the expected result
    result_item = next((item for item in test_metadata if item.get('expected_result') == result), None)

    # If no matching test case is found, raise an error
    if not result_item:
        raise ValueError(f" {result} test case is missing in {test_metadata_path}")

    return result_item


def test_pass_fail_case_added_for_terraform_matcher(terraform_matcher_pass_case):
    """Check if the policy has at least one pass test case"""
    path = terraform_matcher_pass_case['folder_path']
    # Path to the test metadata file
    test_metadata_path = os.path.join(path, 'terraform', 'tests', 'test-metadata.json')

    # Load the test metadata
    test_metadata = test_helpers.load_test_metadata(test_metadata_path)

    # Filter enabled test cases
    enabled_test_metadata = [case for case in test_metadata if case['enabled']]

    # check if any ignore test cases are present,
    # some times a test case is ignored, but it should not be ignored

    valid_test_metadata = []
    for case in enabled_test_metadata:
        ignore = case.get('ignore',False)
        if ignore:
            continue
        valid_test_metadata.append(case)

    # Path to the test cases
    test_path = os.path.join( path, 'terraform','tests')

    # Get a test case that is expected to pass
    test_case = get_case(valid_test_metadata, "PASSED", test_metadata_path)

    # Path to the test file
    test_file = os.path.join(test_path, test_case['filename'])

    # Check if the test file exists
    if not os.path.isfile(test_file):
        pytest.fail("Need to provide at least one pass testcase for policy validation.")

    # Get a test case that is expected to fail
    test_case = get_case(valid_test_metadata, "FAILED",test_metadata_path)

    # Path to the test file
    test_file = os.path.join(test_path, test_case['filename'])

    # Check if the test file exists
    if not os.path.isfile(test_file):
        pytest.fail("Need to provide at least one fail testcase for policy validation.")

    # Iterate over each enabled test case
    for test in valid_test_metadata:
        # Get the description of the test case
        description = test.get('description', '')

        # Check that the description does not contain "TODO"
        assert 'TODO' not in description, f"Description contains TODO, add valid test description: {description}"

    # check if the description of tests are unique
    descriptions = [test['description'] for test in valid_test_metadata]
    # find duplicates from descriptions
    duplicates = set([desc for desc in descriptions if descriptions.count(desc) > 1])
    # Get the filename of the duplicate description
    duplicate_files = [test['filename'] for test in valid_test_metadata if test['description'] in duplicates]
    if duplicate_files:
        pytest.fail(f"Duplicate test descriptions found in files: {duplicate_files}")


def test_pass_fail_case_added_for_cloud_matcher(cloud_matcher_pass_case):
    """Check if the policy has at least one pass test case"""
    path = cloud_matcher_pass_case['folder_path']
    # Path to the test metadata file
    test_metadata_path = os.path.join(path, 'cloud', 'tests', 'test-metadata.json')

    # check if the test metadata file exists
    if not os.path.isfile(test_metadata_path):
        return

    # Load the test metadata
    test_metadata = test_helpers.load_test_metadata(test_metadata_path)

    # Filter enabled test cases
    enabled_test_metadata = [case for case in test_metadata if case['enabled']]

    # check if any ignore test cases are present,
    # some times a test case is ignored, but it should not be ignored

    valid_test_metadata = []
    for case in enabled_test_metadata:
        ignore = case.get('ignore',False)
        if ignore:
            continue
        valid_test_metadata.append(case)

    # Path to the test cases
    test_path = os.path.join( path, 'cloud','tests')

    # Get a test case that is expected to pass
    test_case = get_case(valid_test_metadata, "PASSED", test_metadata_path)

    # Path to the test file
    test_file = os.path.join(test_path, test_case['filename'])

    # Check if the test file exists
    if not os.path.isfile(test_file):
        pytest.fail("Need to provide at least one pass testcase for policy validation.")

    # Get a test case that is expected to fail
    test_case = get_case(valid_test_metadata, "FAILED", test_metadata_path)

    # Path to the test file
    test_file = os.path.join(test_path, test_case['filename'])

    # Check if the test file exists
    if not os.path.isfile(test_file):
        pytest.fail("Need to provide at least one fail testcase for policy validation.")

    # Iterate over each enabled test case
    for test in valid_test_metadata:
        # Get the description of the test case
        description = test.get('description', '')

        # Check that the description does not contain "TODO"
        assert 'TODO' not in description, f"Description contains TODO, add valid test description: {description}"

    # check if the description of tests are unique
    descriptions = [test['description'] for test in valid_test_metadata]
    # find duplicates from descriptions
    duplicates = set([desc for desc in descriptions if descriptions.count(desc) > 1])
    # Get the filename of the duplicate description
    duplicate_files = [test['filename'] for test in valid_test_metadata if test['description'] in duplicates]
    if duplicate_files:
        pytest.fail(f"Duplicate test descriptions found in files: {duplicate_files}")
