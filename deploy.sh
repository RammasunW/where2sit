zip -r "django_deploy-$1.zip" where2sit .ebextensions requirements.txt manage.py -staticfiles

aws s3 cp "django_deploy-$1.zip" s3://rammasunw-where2sit

aws elasticbeanstalk create-application-version --application-name where2sit --source-bundle S3Bucket="rammasunw-where2sit",S3Key="django_deploy-$1.zip" --version-label "ver-$1" --description "deploy-$1" --region "us-east-2"

aws elasticbeanstalk update-environment --environment-name where2sit-environment --version-label "ver-$1" --region "us-east-2"