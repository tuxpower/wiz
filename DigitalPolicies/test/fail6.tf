# S3 bucket is shared publicly via allowing all principals in inline policy for principal AWS [*]
resource "aws_s3_bucket" "fail6" {
  bucket = "a250077-fail6"
  tags = {
    mnd-applicationid      = "APP-250077"
    mnd-dataclassification = "restricted"
  }
}

resource "aws_s3_bucket_policy" "fail6" {
  bucket = aws_s3_bucket.fail6.bucket

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
            "Principal": {
                "AWS": ["*"]
            }
        }
    ]
}
POLICY
}
