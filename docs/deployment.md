# Deployment Guide

## AWS Resources Created
- Elastic Beanstalk Application: `wheretosit`
- Elastic Beanstalk Environment: `wheretosit-environment`
- S3 Buckets:
  - `terraform-state-wheretosit-j-orell` (Terraform state)
  - `j-orell-wheretosit` (deployment artifacts)

## Automated Workflows
1. **Terraform Workflow** - Runs when terraform/ files change
2. **Deploy Workflow** - Runs when application code changes

## Manual Deployment
```bash
# From terraform directory
terraform init
terraform plan
terraform apply