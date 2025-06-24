#!/bin/bash

# Fix GitHub OIDC Setup for NBA Analyzer
set -e

echo "🔧 Fixing GitHub OIDC setup..."

# Configuration
ACCOUNT_ID="950693198730"
REGION="us-east-1"
OIDC_ROLE="GithubOIDCPushToECR"

echo "📋 Creating GitHub OIDC provider..."
# Create the GitHub OIDC provider
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  --region $REGION \
  || echo "OIDC provider already exists"

echo "🔑 Updating OIDC role trust policy..."
# Update the role with the correct trust policy
aws iam update-assume-role-policy \
  --role-name $OIDC_ROLE \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Federated": "arn:aws:iam::950693198730:oidc-provider/token.actions.githubusercontent.com"
        },
        "Action": "sts:AssumeRoleWithWebIdentity",
        "Condition": {
          "StringEquals": {
            "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
          },
          "StringLike": {
            "token.actions.githubusercontent.com:sub": "repo:madelinesanders/nba-analyzer:*"
          }
        }
      }
    ]
  }' \
  --region $REGION

echo "✅ OIDC setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Push a new commit to trigger the workflow again"
echo "2. The OIDC authentication should now work" 