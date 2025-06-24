#!/bin/bash

# NBA Analyzer AWS Setup Script
# This script creates the required AWS resources for the Lambda deployment

set -e

echo "🚀 Setting up AWS resources for NBA Analyzer..."

# Configuration
ACCOUNT_ID="950693198730"
REGION="us-east-1"
ECR_REPO="nba-etl-lambda"
LAMBDA_FUNCTION="nba-etl-lambda"
S3_BUCKET="nba-analyzer-data-madeline"
OIDC_ROLE="GithubOIDCPushToECR"
LAMBDA_ROLE="lambda-execution-role"

echo "📋 Creating ECR repository..."
aws ecr create-repository \
  --repository-name $ECR_REPO \
  --region $REGION \
  --image-scanning-configuration scanOnPush=true \
  || echo "ECR repository already exists"

echo "🪣 Creating S3 bucket..."
aws s3 mb s3://$S3_BUCKET --region $REGION \
  || echo "S3 bucket already exists"

echo "🔐 Creating Lambda execution role..."
# Create the role
aws iam create-role \
  --role-name $LAMBDA_ROLE \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }' \
  || echo "Lambda role already exists"

# Attach basic execution policy
aws iam attach-role-policy \
  --role-name $LAMBDA_ROLE \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
  || echo "Basic execution policy already attached"

# Create S3 access policy
aws iam put-role-policy \
  --role-name $LAMBDA_ROLE \
  --policy-name S3AccessPolicy \
  --policy-document "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [
      {
        \"Effect\": \"Allow\",
        \"Action\": [
          \"s3:GetObject\",
          \"s3:PutObject\",
          \"s3:DeleteObject\"
        ],
        \"Resource\": \"arn:aws:s3:::$S3_BUCKET/*\"
      }
    ]
  }" \
  || echo "S3 access policy already exists"

echo "🔑 Creating OIDC role for GitHub Actions..."
# Create the OIDC role
aws iam create-role \
  --role-name $OIDC_ROLE \
  --assume-role-policy-document file://github-oidc-trust.json \
  || echo "OIDC role already exists"

# Attach ECR and Lambda policies
aws iam attach-role-policy \
  --role-name $OIDC_ROLE \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser \
  || echo "ECR policy already attached"

aws iam attach-role-policy \
  --role-name $OIDC_ROLE \
  --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess \
  || echo "Lambda policy already attached"

echo "⚡ Creating Lambda function..."
# Wait for role to be available
sleep 10

aws lambda create-function \
  --function-name $LAMBDA_FUNCTION \
  --package-type Image \
  --code ImageUri=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest \
  --role arn:aws:iam::$ACCOUNT_ID:role/$LAMBDA_ROLE \
  --timeout 900 \
  --memory-size 1024 \
  --region $REGION \
  || echo "Lambda function already exists"

echo "✅ AWS setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Push your code to the 'dev' branch"
echo "2. Monitor the GitHub Actions workflows"
echo "3. Check Lambda logs in CloudWatch"
echo ""
echo "🔗 Useful links:"
echo "- GitHub Actions: https://github.com/madelinesanders/nba-analyzer/actions"
echo "- ECR Repository: https://console.aws.amazon.com/ecr/repositories/$ECR_REPO"
echo "- Lambda Function: https://console.aws.amazon.com/lambda/home?region=$REGION#/functions/$LAMBDA_FUNCTION"
echo "- S3 Bucket: https://s3.console.aws.amazon.com/s3/buckets/$S3_BUCKET" 