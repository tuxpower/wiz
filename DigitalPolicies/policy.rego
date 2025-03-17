# logic: "S3Bucket should not have (acl.grants contain [uri like 'http://acs.amazonaws.com/groups/global/%'] or policy.Statement contain [Effect='Allow' and (Principal='*' or Principal.AWS='*')])"

package wiz
import data.generic.common as common_lib
import data.generic.terraform as terraLib
# condition:
# S3Bucket should not have (acl.grants contain [uri like 'http://acs.amazonaws.com/groups/global/%'] or
# policy.Statement contain [Effect='Allow' and (Principal='*' or Principal.AWS='*')])

# ##################ALL PRINCIPALS#############################################
principalKeys := {"Principal", "Principals"}

wildcardPrincipal(statement) {
	common_lib.equalsOrInArray(statement[principalKeys[_]].AWS, "*")
}{
	common_lib.equalsOrInArray(statement[principalKeys[_]], "*")
}{
	common_lib.equalsOrInArray(statement[principalKeys[_]]["*"], "*")
}

policyShouldNotAllowAllPrincipals(policy) {
	st := common_lib.get_statement(policy)
    statement := st[_]
    lower(statement.Effect) == "allow"
  	wildcardPrincipal(statement)
}
bucketPolicyShouldNotAllowAllPrincipals(document,s3Bucket, s3Name){
	terraLib.validKey(s3Bucket, "policy")
	policy := common_lib.json_unmarshal(s3Bucket.policy)
    policyShouldNotAllowAllPrincipals(policy)
} {
# 	not terraLib.validKey(s3Bucket, "policy")
	s3Policy := document.resource.aws_s3_bucket_policy[policyName]
	terraLib.associatedResources(s3Bucket, s3Policy, s3Name, policyName, "bucket", "bucket")
	terraLib.validKey(s3Policy, "policy")
    policy := common_lib.json_unmarshal(s3Policy.policy)
	policyShouldNotAllowAllPrincipals(policy)
}

WizPolicy[result] {
	document := input.document[i]
	resource := document.resource.aws_s3_bucket[name]
    bucketPolicyShouldNotAllowAllPrincipals(document,resource, name)
	result := {
		"documentId": document.id,
		"resourceName": terraLib.get_resource_name(resource, name),
		"searchKey": sprintf("aws_s3_bucket[%s]", [  name]),
		"keyExpectedValue": sprintf("aws_s3_bucket[%s] should not allow all principals", [name]),
		"keyActualValue": sprintf("aws_s3_bucket[%s] allows all principals", [name]),
		"resourceTags": object.get(resource, "tags", {}),
	}
}
# ##################ALL PRINCIPALS#############################################


# ##################GLOBAL URI#############################################
allUserURI := "http://acs.amazonaws.com/groups/global/"

UriCheck(grants) {
    startswith(lower(grants[grant].uri), allUserURI)
}{
	grantees := terraLib.getArray(grants[grant].grantee)
	startswith(lower(grantees[_].uri), allUserURI)
}

aclDoesNotAllowGlobalURIOld(document, bucket, bucketName) {
	# Support for old TF versions
	grants := terraLib.getArray(bucket.grant)
	UriCheck(grants)
}
aclDoesNotAllowGlobalURINew(document, bucket, bucketName) {
	# Support for new TF versions
	aclResource := document.resource.aws_s3_bucket_acl[aclName]
	terraLib.associatedResources(bucket, aclResource, bucketName, aclName, "bucket", "bucket")
	accessControlPolicy := terraLib.getArray(aclResource.access_control_policy)[acp]
	grants := terraLib.getArray(accessControlPolicy.grant)
	UriCheck(grants)
}
bucketACLDoesNotAllowAllUsersURI(document, s3Bucket, s3Name) {
	# Support for old TF versions
	aclDoesNotAllowGlobalURIOld(document, s3Bucket, s3Name)
} {
    aclDoesNotAllowGlobalURINew(document, s3Bucket, s3Name)
} 

WizPolicy[result] {
	document := input.document[i]
	resource := document.resource.aws_s3_bucket[name]
	bucketACLDoesNotAllowAllUsersURI(document, resource, name)
	
	result := {
		"documentId": document.id,
		"resourceName": terraLib.get_resource_name(resource, name),
		"searchKey": sprintf("aws_s3_bucket[%s]", [name]),
		"keyExpectedValue": sprintf("aws_s3_bucket[%s] ACL should not grant global uri starts with %s", [name,allUserURI]),
		"keyActualValue": sprintf("aws_s3_bucket[%s] ACL grants global uri starts with %s", [name, allUserURI]),
		"resourceTags": object.get(resource, "tags", {}),
	}
}
# ##################GLOBAL URI#############################################
