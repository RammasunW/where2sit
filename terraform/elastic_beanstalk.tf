data "aws_elastic_beanstalk_solution_stack" "python311" {
  most_recent = true
  # Platform strings change over time; pick latest AL2023 + Python 3.11 in this region.
  name_regex = "^64bit Amazon Linux 2023 v[0-9.]+ running Python 3\\.11$"
}

resource "aws_elastic_beanstalk_application" "where2sit" {
  name        = "where2sit"
  description = "Campus room availability tracker"
}

resource "aws_elastic_beanstalk_environment" "where2sit_env" {
  name                = "where2sit-environment"
  application         = aws_elastic_beanstalk_application.where2sit.name
  solution_stack_name = data.aws_elastic_beanstalk_solution_stack.python311.name
  cname_prefix          = "moham-where2sit"

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
