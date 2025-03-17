resource "aws_s3_bucket" "fail2" {
  bucket = "a250077-fail2"
}

resource "aws_s3_bucket_policy" "policy" {
  bucket = aws_s3_bucket.fail2.id
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
      "arn:aws:s3:::a250077-fail2/*",
    ]
  }
}
