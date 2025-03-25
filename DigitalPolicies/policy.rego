package wiz

import data.generic.terraform as terra_lib
import data.generic.common as common_lib
import future.keywords.in

isHighlyRestricted(resource) {
	tags := object.get(resource, "tags", {})
    tags["mnd-dataclassification"] == "highlyrestricted" 
}

isRestricted(resource) {
	tags := object.get(resource, "tags", {})
    tags["mnd-dataclassification"] == "restricted" 
}

is_tag_matching(tag_value) {
      tags_to_match := { "restricted","highlyrestricted" }
      tag_value in tags_to_match
}

# fail if attribute storage_encrypted is not defined
WizPolicy[result] {
	
	document := input.document[i]
	resource := document.resource.aws_db_instance[name]
	tags := object.get(resource, "tags", {})
	is_tag_matching(tags["mnd-dataclassification"])
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
		"resourceTags": object.get(resource, "tags", {}),
	}
}

# fail if attribute storage_encrypted is not set to true
WizPolicy[result] {
	document := input.document[i]
	resource := document.resource.aws_db_instance[name]
	isRestricted(resource)
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
		"resourceTags": object.get(resource, "tags", {}),
	}
}

WizPolicy[result] {
	document := input.document[i]
	resource := document.resource.aws_db_instance[name]
	isHighlyRestricted(resource)
	object.get(resource, "kms_key_id", null) == null	
	
    result := {
		"documentId": document.id,
		"searchKey": sprintf("aws_db_instance[%s]", [name]),
		"keyExpectedValue": sprintf("'aws_db_instance[%s].kms_key_id' should be defined and contain an ARN of a KMS encryption key", [name]),
		"keyActualValue": sprintf("'aws_db_instance[%s].kms_key_id' is undefined or 'null'", [name]),
		"resourceTags": object.get(resource, "tags", {}),
		"issueType": "MissingAttribute",
	}
}
