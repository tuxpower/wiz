package wiz

import data.generic.terraform as terra_lib
import data.generic.common as common_lib
import future.keywords.in

# Function to check if the tag value matches the required patterns
is_tag_matching(tag_value) {
    tags_to_match := { "restricted", "highlyrestricted" }
    tag_value in tags_to_match
}

# Function to check if the tag key and value match the required regex patterns
is_regex_tag_matching(tags) {
    some key, value
    regex.match("(?i)([mnd-]?Data[_]?Classification)", key)  # case-insensitive match for key
    regex.match("(?i)Highly[_]?Restricted", value)           # case-insensitive match for value
    tags[key] == value
}

# fail if attribute storage_encrypted is not defined
WizPolicy[result] {
    document := input.document[i]
    resource := document.resource.aws_db_instance[name]
    tags := object.get(resource, "tags", {})
    is_tag_matching(tags["mnd-dataclassification"]) or is_regex_tag_matching(tags)
    not common_lib.valid_key(resource, "storage_encrypted")

    result := {
        "documentId": document.id,
        "searchKey": sprintf("aws_db_instance[%s]", [name]),
        "keyExpectedValue": sprintf("'aws_db_instance[%s].storage_encrypted' should be set to 'true'", [name]),
        "keyActualValue": sprintf("'aws_db_instance[%s].storage_encrypted' is undefined", [name]),
        "remediation": json.marshal({
            "before": "false",
            "after": "true"
        }),
        "resourceTags": tags,
    }
}

# fail if attribute storage_encrypted is not set to true
WizPolicy[result] {
    document := input.document[i]
    resource := document.resource.aws_db_instance[name]
    tags := object.get(resource, "tags", {})
    is_tag_matching(tags["mnd-dataclassification"]) or is_regex_tag_matching(tags)
    common_lib.valid_key(resource, "storage_encrypted")
    isFalse := {false, "false"}
    resource.storage_encrypted in isFalse

    result := {
        "documentId": document.id,
        "searchKey": sprintf("aws_db_instance[%s]", [name]),
        "keyExpectedValue": sprintf("'aws_db_instance[%s].storage_encrypted' should be set to 'true'", [name]),
        "keyActualValue": sprintf("'aws_db_instance[%s].storage_encrypted' is not set to 'true'", [name]),
        "remediation": json.marshal({
            "before": "false",
            "after": "true"
        }),
        "resourceTags": tags,
    }
}

# fail if attribute kms_key_id is not defined for highly restricted resources
WizPolicy[result] {
    document := input.document[i]
    resource := document.resource.aws_db_instance[name]
    tags := object.get(resource, "tags", {})
    is_tag_matching(tags["mnd-dataclassification"]) or is_regex_tag_matching(tags)
    object.get(resource, "kms_key_id", null) == null

    result := {
        "documentId": document.id,
        "searchKey": sprintf("aws_db_instance[%s]", [name]),
        "keyExpectedValue": sprintf("'aws_db_instance[%s].kms_key_id' should be defined and contain an ARN of a KMS encryption key", [name]),
        "keyActualValue": sprintf("'aws_db_instance[%s].kms_key_id' is undefined or 'null'", [name]),
        "resourceTags": tags,
        "issueType": "MissingAttribute",
    }
}
