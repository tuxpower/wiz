resource "aws_ecs_service" "pass1" {
  name = "example"

  volume_configuration {
    name = "example"
    managed_ebs_volume {
      role_arn = aws_iam_role.example.arn
      kms_key_id = aws_kms_key.kms_key.key_id
      tag_specifications {
        resource_type = "volume"
        tags = {
          mnd-dataclassification = "highlyrestricted"
        }
      }
    }
  }
}

resource "aws_kms_key" "kms_key" {
  description             = "An example symmetric encryption KMS key"
  enable_key_rotation     = true
  deletion_window_in_days = 20
}

resource "aws_iam_role" "example" {
  name = "example"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

