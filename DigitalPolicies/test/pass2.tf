# S3 bucket is not shared publicly via bucket ACL or bucket policy
resource "aws_s3_bucket" "pass2" {
  bucket = "a250077-pass2"
  tags = {
    mnd-applicationid      = "APP-250077"
    mnd-dataclassification = "restricted"
  }
}
resource "aws_s3_bucket_acl" "pass2" {
  bucket = aws_s3_bucket.pass2.bucket
  acl    = "private"
}

