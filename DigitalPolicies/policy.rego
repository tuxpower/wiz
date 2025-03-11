# logic: "ApplicationLoadBalancer where isPublic = 'false' and listeners contain [ protocol='HTTPS' ] should have listeners contain [ securityPolicy like 'ELBSecurityPolicy-TLS-1-2-%' or securityPolicy like 'ELBSecurityPolicy-TLS13-%' or securityPolicy like 'ELBSecurityPolicy-FS-1-2-%']",
# logic: "ApplicationLoadBalancer where isPublic = 'true' and listeners contain [ protocol='HTTPS' ] should have listeners contain [ securityPolicy like 'ELBSecurityPolicy-TLS-1-2-%' or securityPolicy like 'ELBSecurityPolicy-TLS13-%' or securityPolicy like 'ELBSecurityPolicy-FS-1-2-%']",
package wiz

import data.generic.terraform as terraLib
import data.generic.common as commonLib
import future.keywords.in

lbResources := {"aws_lb", "aws_alb"}
lbListenerResources := {"aws_lb_listener", "aws_alb_listener"}

secureProtocols := {"HTTPS", "TLS"}

sslPolicyStartsWith(ssl_policy) {
	not startswith(ssl_policy, "ELBSecurityPolicy-FS-1-2")
	not startswith(ssl_policy, "ELBSecurityPolicy-TLS-1-2")
	not startswith(ssl_policy, "ELBSecurityPolicy-TLS13")
}

albProtocolIsHttp(document, lbResource, lbResourceName) {
	lbListenerResource := document.resource[lbListenerResources[idx]][lbListenerName]
	terraLib.associatedResources(lbResource, lbListenerResource, lbResourceName, lbListenerName, null, "load_balancer_arn") 
	lower(lbListenerResource.protocol) == "http"
}

albRedirectMissing(document, lbResource, lbResourceName) {
	lbListenerResource := document.resource[lbListenerResources[idx]][lbListenerName]
	terraLib.associatedResources(lbResource, lbListenerResource, lbResourceName, lbListenerName, null, "load_balancer_arn") 
	not terraLib.validKey(lbListenerResource.default_action, "redirect")
}

albRedirectHTTPS(document, lbResource, lbResourceName) {
	lbListenerResource := document.resource[lbListenerResources[idx]][lbListenerName]
	terraLib.associatedResources(lbResource, lbListenerResource, lbResourceName, lbListenerName, null, "load_balancer_arn") 
	terraLib.validKey(lbListenerResource.default_action, "redirect")
    terraLib.validKey(lbListenerResource.default_action.redirect, "protocol")
    lbListenerResource.default_action.redirect.protocol == "HTTPS"
}

albInSecureProtocols(document, lbResource, lbResourceName) {
	lbListenerResource := document.resource[lbListenerResources[i]][lbListenerName]
	terraLib.associatedResources(lbResource, lbListenerResource, lbResourceName, lbListenerName, null, "load_balancer_arn") 
	lbListenerResource.protocol in secureProtocols
}

albHasSSLPolicyDefined(document, lbResource, lbResourceName) {
	lbListenerResource := document.resource[lbListenerResources[i]][lbListenerName]
	terraLib.associatedResources(lbResource, lbListenerResource, lbResourceName, lbListenerName, null, "load_balancer_arn") 
	terraLib.validKey(lbListenerResource, "ssl_policy")
}

albWithUnsecureSSLPolicy(document, lbResource, lbResourceName) {
	lbListenerResource := document.resource[lbListenerResources[i]][lbListenerName]
	terraLib.associatedResources(lbResource, lbListenerResource, lbResourceName, lbListenerName, null, "load_balancer_arn") 
	lbListenerResource.protocol in secureProtocols
    terraLib.validKey(lbListenerResource, "ssl_policy")
	sslPolicyStartsWith(lbListenerResource.ssl_policy)
    
}

WizPolicy[result] {
	document := input.document[i]
	lbResource := document.resource[lbResources[lb]][lbResourceName]
	object.get(lbResource, "load_balancer_type", "application") == "application"	
    albProtocolIsHttp(document, lbResource, lbResourceName)
    albRedirectMissing(document, lbResource, lbResourceName)
	result := {  
		"documentId": document.id,
		"searchKey": sprintf("%s[%s]", [lbResources[lb], lbResourceName]),
		"keyExpectedValue": sprintf("%s[%s].default_action.redirect.protocol' should be equal to 'HTTPS'",[lbResources[lb], lbResourceName]),
		"keyActualValue": sprintf("%s[%s].default_action.redirect.protocol' is missing",[lbResources[lb], lbResourceName]),
		"resourceTags": object.get(lbResource, "tags", {}),
	}
}

WizPolicy[result] {
	document := input.document[i]
	lbResource := document.resource[lbResources[lb]][lbResourceName]
	object.get(lbResource, "load_balancer_type", "application") == "application"	
    albProtocolIsHttp(document, lbResource, lbResourceName)
    not albRedirectHTTPS(document, lbResource, lbResourceName)
	result := {  
		"documentId": document.id,
		"searchKey": sprintf("%s[%s]", [lbResources[lb], lbResourceName]),
		"keyExpectedValue": "default_action.redirect.protocol' should be equal to 'HTTPS'",
		"keyActualValue": "default_action.redirect.protocol' is equal to 'HTTPS'",
		"resourceTags": object.get(lbResource, "tags", {}),
	}
}

WizPolicy[result] {
	document := input.document[i]
	lbResource := document.resource[lbResources[lb]][lbResourceName]
	object.get(lbResource, "load_balancer_type", "application") == "application"
    albInSecureProtocols(document, lbResource, lbResourceName)
	not albHasSSLPolicyDefined(document, lbResource, lbResourceName)
	result := {    	
		"documentId": document.id,
		"searchKey": sprintf("%s[%s]", [lbResources[lb], lbResourceName]),
		"keyExpectedValue": "All listeners with 'protocol' set to 'HTTPS' or 'TLS' must have ssl policies defined",
		"keyActualValue": "At least one listener with 'protocol' set to 'HTTPS' or 'TLS' has ssl policy undefined",
		"resourceTags": object.get(lbResource, "tags", {}),
	}
}

WizPolicy[result] {
	document := input.document[i]
	lbResource := document.resource[lbResources[lb]][lbResourceName]
	object.get(lbResource, "load_balancer_type", "application") == "application"	
    albWithUnsecureSSLPolicy(document, lbResource, lbResourceName)
    
	result := {
		"documentId": document.id,
		"searchKey": sprintf("%s[%s]", [lbResources[lb], lbResourceName]),
		"keyExpectedValue": "All listeners with 'protocol' set to 'HTTPS' or 'TLS' must use ssl policies starts with 'ELBSecurityPolicy-FS-1-2' or 'ELBSecurityPolicy-TLS-1-2' or 'ELBSecurityPolicy-TLS13'",
		"keyActualValue": "At least one listener with 'protocol' set to 'HTTPS' or 'TLS' is not using ssl policies starting with 'ELBSecurityPolicy-FS-1-2' or 'ELBSecurityPolicy-TLS-1-2' or 'ELBSecurityPolicy-TLS13'",
		"resourceTags": object.get(lbResource, "tags", {}),
	}
}

