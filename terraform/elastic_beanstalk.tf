resource "aws_elastic_beanstalk_application" "application" {
  name = "where2sit"
}

resource "aws_elastic_beanstalk_environment" "environment" {
  name                = "where2sit-environment"
  cname_prefix        = "rammasunwwhere2sit"
  application         = aws_elastic_beanstalk_application.application.name
  solution_stack_name = "64bit Amazon Linux 2023 v4.12.1 running Python 3.13"
  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = "aws-elasticbeanstalk-ec2-role"
  }
}