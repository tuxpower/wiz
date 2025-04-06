resource "aws_ecs_service" "fail3" {
  name = "example"

  volume_configuration {
    name = "example"
    managed_ebs_volume {
      role_arn = aws_iam_role.example.arn
      encrypted = false
      tag_specifications {
        resource_type = "volume"
        tags = {
          mnd-dataclassification = "restricted"
        }
      }
    }
  }
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

