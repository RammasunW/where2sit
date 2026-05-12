terraform {
  backend "s3" {
    bucket = "terraform-state-where2sit-mohammed-521330944457-us-east-2-an"
    key    = "terraform/state"
    region = "us-east-2"
  }
}
