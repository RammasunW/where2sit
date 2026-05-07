resource "aws_elastic_beanstalk_application" "where2sit" {
  name        = "where2sit"
  description = "Campus room availability tracker"
}

resource "aws_elastic_beanstalk_environment" "where2sit_env" {
  name                = "j-orell-where2sit-env"
  application         = aws_elastic_beanstalk_application.where2sit.name
  solution_stack_name = "64bit Amazon Linux 2023 v4.3.0 running Python 3.11"
  cname_prefix        = "j-orell-where2sit"

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = "aws-elasticbeanstalk-ec2-role"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DJANGO_SETTINGS_MODULE"
    value     = "wheretosit.settings"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DEBUG"
    value     = "False"
  }
}