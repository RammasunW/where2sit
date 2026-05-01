terraform {
  backend "s3" {
    bucket = "terraform-state-where2sit-j-orell"
    key    = "terraform/state"
    region = "us-east-1"
  }
}