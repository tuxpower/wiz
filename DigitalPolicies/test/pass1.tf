# S3 bucket is not shared publicly via bucket ACL or bucket policy
resource "aws_s3_bucket" "pass1" {
  bucket = "a250077-pass1"
  tags = {
    mnd-applicationid      = "APP-250077"
    mnd-dataclassification = "restricted"
  }
}

resource "aws_s3_bucket_policy" "policy" {
  bucket = aws_s3_bucket.pass1.id
  policy = data.aws_iam_policy_document.policy.json
}

data "aws_iam_policy_document" "policy" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["123456789012"]
    }

    actions = [
      "s3:GetObject",
    ]

    resources = [
      "arn:aws:s3:::a250077-pass1/*",
    ]
  }
}
