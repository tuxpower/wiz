i# S3 bucket ACL grants global uri starts with http://acs.amazonaws.com/groups/global/
resource "aws_s3_bucket" "fail1" {
  bucket = "a250077-fail1"
  tags = {
    mnd-applicationid      = "APP-250077"
    mnd-dataclassification = "restricted"
  }
}
resource "aws_s3_bucket_acl" "fail1" {
  bucket = aws_s3_bucket.fail1.bucket
  access_control_policy {
    grant {
      grantee {
        id   = "52b113e7a2f25102679df27bb0ae12b3f85be6"
        type = "CanonicalUser"
      }
      permission = "READ"
    }
    grant {
      grantee {
        type = "Group"
        uri  = "http://acs.amazonaws.com/groups/global/AuthenticatedUsers"
      }
      permission = "READ_ACP"
    }
    owner {
      id = data.aws_canonical_user_id.current.id
    }
  }
}
