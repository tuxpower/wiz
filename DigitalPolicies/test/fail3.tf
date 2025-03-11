# ALB Listener using HTTP protocol must define default_action.redirect.protocol set to HTTPS
resource "aws_lb" "fail3" {
  name                       = "a250077-fail3"
  internal                   = true
  load_balancer_type         = "application"
  subnets                    = [aws_subnet.subnet_az1.id]
  enable_deletion_protection = false

}

resource "aws_lb_listener" "fail3" {
  load_balancer_arn = aws_lb.fail3.arn
  protocol          = "HTTP"
  port              = "80"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fail3.arn
  }
}
resource "aws_lb_target_group" "fail3" {
  name     = "a250077-fail3"
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
