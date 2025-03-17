# S3 bucket is not shared publicly via bucket ACL or bucket policy
resource "aws_s3_bucket" "pass3" {
  bucket = "a250077-pass3"
  tags = {
    mnd-applicationid      = "APP-250077"
    mnd-dataclassification = "restricted"
  }
}

resource "aws_s3_bucket_policy" "pass3" {
  bucket = aws_s3_bucket.pass3.bucket

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
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::a250077-pass3/*",
            "Condition": {
                "IpAddress": {"aws:SourceIp": "8.8.8.8/32"}
            }
        }
    ]
}
POLICY
}
