# S3 bucket is not shared publicly via bucket ACL or bucket policy
resource "aws_s3_bucket" "pass4" {
  bucket = "a250077-pass4"
  tags = {
    mnd-applicationid      = "APP-250077"
    mnd-dataclassification = "restricted"
  }

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Deny",
            "Resource": "arn:aws:s3:::a250077-pass4/*",
            "Principal": "*"
        }
    ]
}
POLICY
}

