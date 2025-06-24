# NBA Analyzer - Lambda + Docker + GitHub Actions Setup Guide

## Architecture Overview

This project uses AWS Lambda with Docker containers, deployed via GitHub Actions:

```
GitHub Push → Build Docker Image → Push to ECR → Deploy to Lambda → Schedule Execution
```

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **GitHub Repository** with OIDC configured
3. **ECR Repository** created: `nba-etl-lambda`
4. **S3 Bucket** created: `nba-analyzer-data-madeline`

## AWS Setup Required

### 1. Create ECR Repository
```bash
aws ecr create-repository --repository-name nba-etl-lambda --region us-east-1
```

### 2. Create Lambda Function
```bash
aws lambda create-function \
  --function-name nba-etl-lambda \
  --package-type Image \
  --code ImageUri=950693198730.dkr.ecr.us-east-1.amazonaws.com/nba-etl-lambda:latest \
  --role arn:aws:iam::950693198730:role/lambda-execution-role \
  --timeout 900 \
  --memory-size 1024
```

### 3. Create Lambda Execution Role
Create an IAM role with these policies:
- `AWSLambdaBasicExecutionRole`
- Custom policy for S3 access to your bucket
- Custom policy for ECR access

### 4. Update OIDC Trust Policy
Replace the placeholder values in `github-oidc-trust.json`:
- Replace `<madelinesanders>` with your actual GitHub username
- Replace `<nba-analyzer>` with your actual repository name

## GitHub Actions Workflows

### 1. Build and Push (`build-and-push.yml`)
- Triggers on push to `dev` branch
- Builds Docker image from your Dockerfile
- Pushes to ECR

### 2. Deploy Lambda (`deploy-lambda.yml`)
- Triggers after successful build
- Updates Lambda function with new image
- Tests the function

### 3. Schedule Execution (`schedule-lambda.yml`)
- Runs every Monday at 8 AM ET
- Manually triggerable
- Invokes Lambda function

## Deployment Steps

1. **Update OIDC Trust Policy** with your actual GitHub username and repo name
2. **Create ECR Repository** in AWS
3. **Create Lambda Function** in AWS
4. **Push to dev branch** to trigger the pipeline
5. **Monitor the workflows** in GitHub Actions

## Troubleshooting

### Common Issues:

1. **OIDC Trust Policy Error**: Make sure your GitHub username and repo name are correct
2. **ECR Push Error**: Ensure the ECR repository exists
3. **Lambda Update Error**: Ensure the Lambda function exists
4. **Permission Errors**: Check IAM roles and policies

### Debug Commands:

```bash
# Check ECR repository
aws ecr describe-repositories --repository-names nba-etl-lambda

# Check Lambda function
aws lambda get-function --function-name nba-etl-lambda

# Check IAM role
aws iam get-role --role-name GithubOIDCPushToECR
```

## Alternative: Direct GitHub Actions (Simpler)

If Lambda is too complex, you can use the existing `nba-etl.yml` workflow which runs the ETL directly in GitHub Actions. This is simpler but less scalable.

## Next Steps

1. Update the OIDC trust policy with your actual values
2. Create the required AWS resources
3. Push to the dev branch to test the pipeline
4. Monitor the GitHub Actions workflows
5. Check the Lambda logs in CloudWatch 