# ALB Listener using TCP protocol is ignored
resource "aws_lb" "pass4" {
  name                       = "a250077-pass4"
  internal                   = false
  load_balancer_type         = "application"
  subnets                    = [aws_subnet.subnet_az1.id]
  enable_deletion_protection = false

}

resource "aws_lb_listener" "pass4" {
  load_balancer_arn = aws_lb.pass4.arn
  protocol          = "TCP"
  port              = "8080"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.pass4.arn
  }
}
resource "aws_lb_target_group" "pass4" {
  name     = "a250077-pass4"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.vpc.id

  health_check {
    port     = 80
    protocol = "http"
  }

  lifecycle {
    create_before_destroy = true
  }
}

data "aws_availability_zones" "azs" {
  state = "available"
}

resource "aws_vpc" "vpc" {
  cidr_block = "192.168.0.0/22"
}

resource "aws_subnet" "subnet_az1" {
  availability_zone = data.aws_availability_zones.azs.names[0]
  cidr_block        = "192.168.0.0/24"
  vpc_id            = aws_vpc.vpc.id
}
