resource "aws_db_instance" "fail1" {
  allocated_storage    = 10
  db_name              = "a250077-fail1"
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t3.micro"
  username             = "foo"
  password             = "foobarbaz"
  parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
  publicly_accessible  = true
  tags = {
    mnd-applicationid = "APP-250077"
    mnd-owner         = "babitha.mathew@lseg.com"
    mnd-dataclassification = "restricted"
  }
  storage_encrypted = true
}
