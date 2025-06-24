#!/bin/bash

# Simple OIDC fix
set -e

echo "🔧 Simple OIDC fix..."

# Update the trust policy with a more permissive condition
aws iam update-assume-role-policy \
  --role-name GithubOIDCPushToECR \
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
            "token.actions.githubusercontent.com:sub": "repo:madelinesanders/*"
          }
        }
      }
    ]
  }'

echo "✅ Trust policy updated with more permissive condition!"
echo ""
echo "📝 Next steps:"
echo "1. Push a new commit to trigger the workflow again"
echo "2. If this works, we can make it more specific later" 