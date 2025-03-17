# S3 bucket is shared publicly via allowing all principals with aws_s3_bucket_policy for principal *
resource "aws_s3_bucket" "fail5" {
  bucket = "a250077-fail5"
  tags = {
    mnd-applicationid      = "APP-250077"
    mnd-dataclassification = "restricted"
  }
}

resource "aws_s3_bucket_policy" "fail5" {
  bucket = aws_s3_bucket.fail5.bucket

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
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": "*"
        }
    ]
}
POLICY
}
