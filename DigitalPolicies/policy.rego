package wiz

import data.generic.terraform as terra_lib
import data.generic.common as common_lib

rdsResources := {"aws_db_instance", "aws_rds_cluster_instance"}

WizPolicy[result] {
	document := input.document[i]
	rdsResource := document.resource[rdsResources[idx]][name]
	not terra_lib.validKey(rdsResource, "publicly_accessible")

    result := {
		"documentId": input.document[i].id,
		"searchKey": sprintf("%s[%s].publicly_accessible", [rdsResources[idx], name]),
		"keyExpectedValue": sprintf("%s[%s].publicly_accessible should be defined and not null", [rdsResources[idx],name]),
		"keyActualValue": sprintf("%s[%s].publicly_accessible is undefined or null", [rdsResources[idx], name]),
		"resourceTags": object.get(rdsResource, "tags", {}),
		"issueType": "MissingAttribute",
		"remediation": "publicly_accessible = false",
		"remediationType": "addition",

	}
}

WizPolicy[result] {
	document := input.document[i]
	rdsResource := document.resource[rdsResources[idx]][name]
	rdsResource.publicly_accessible == true
    result := {
		"documentId": input.document[i].id,
		"searchKey": sprintf("%s[%s].publicly_accessible", [rdsResources[idx], name]),
		"keyExpectedValue": sprintf("%s[%s].publicly_accessible should be 'false'", [rdsResources[idx],name]),
		"keyActualValue": sprintf("%s[%s].publicly_accessible is 'true'", [rdsResources[idx], name]),
		"remediation": json.marshal({
			"before": "true",
			"after": "false"
		}),
		"remediationType": "update",
		"resourceTags": object.get(rdsResource, "tags", {}),
	}
}
