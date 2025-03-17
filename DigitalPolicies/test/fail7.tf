# S3 bucket is shared publicly via allowing all principals with aws_s3_bucket_policy for principal AWS [*]
resource "aws_s3_bucket" "fail7" {
  bucket = "a250077-fail7"
  tags = {
    mnd-applicationid      = "APP-250077"
    mnd-dataclassification = "restricted"
  }
}

resource "aws_s3_bucket_policy" "policy" {
  bucket = aws_s3_bucket.fail7.id
  policy = data.aws_iam_policy_document.policy.json
}

data "aws_iam_policy_document" "policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions   = ["s3:GetObject"]
    resources = ["*"]
  }
}
