import boto3
import os

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
)

s3.upload_file("stats_df.csv", "nba-analyzer-data-madeline", "nba-data/stats_df.csv")

print("Uploaded to S3 from GitHub Actions")