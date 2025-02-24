package wiz

import data.generic.common as common_lib
import data.generic.terraform as terraLib

matches(shield, name) {
	attribute = terraLib.getValueArrayOrObject(shield.resource_arn)
	split(attribute,".")[1] == name
} else {
	attribute = terraLib.getValueArrayOrObject(shield.resource_arn)
	target := split(attribute,"/")[1]
	split(target,".")[1] == name
}

has_shield_advanced(name) {
	shield := input.document[_].resource.aws_shield_protection[_]
	matches(shield, name)
}

 
# policy to check cloudfront has shield protection
WizPolicy[result] {
	target := input.document[i].resource.aws_cloudfront_distribution[name]
   	not has_shield_advanced(name)

	result := {
		"documentId": input.document[i].id,
		"resourceName": terraLib.get_resource_name(target, name),
		"searchKey": sprintf("aws_cloudfront_distribution[%s]", [name]),
		"issueType": "MissingAttribute",
		"keyExpectedValue": sprintf("aws_cloudfront_distribution[%s] has shield advanced associated", [name]),
		"keyActualValue": sprintf("aws_cloudfront_distribution[%s] does not have shield advanced associated", [name]),
		"searchLine": common_lib.build_search_line(["resource", "aws_cloudfront_distribution", name], []),
		"resourceTags": object.get(target, "tags", {}),
	}
}

# policy to check cloudfront has WAF enabled
WizPolicy[result] {
	resource := input.document[i].resource.aws_cloudfront_distribution[name]
	resource.enabled == true
	not resource.web_acl_id

	result := {
		"documentId": input.document[i].id,
		"resourceName": terraLib.get_resource_name(resource, name),
		"searchKey": sprintf("aws_cloudfront_distribution[%s].web_acl_id", [name]),
		"issueType": "MissingAttribute",
		"keyExpectedValue":sprintf("aws_cloudfront_distribution[%s] has web_acl_id", [name]),
		"keyActualValue": sprintf("aws_cloudfront_distribution[%s] does not have web_acl_id", [name]),
		"resourceTags": object.get(resource, "tags", {}),
	}
}
