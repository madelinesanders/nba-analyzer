#!/bin/bash
# Check if the user exists
airflow users list | grep -q "madeline@example.com"
if [ $? -ne 0 ]; then
  echo "Creating admin user..."
  airflow users create \
    --username madeline \
    --firstname Madeline \
    --lastname Sanders \
    --role Admin \
    --email madeline@example.com \
    --password "${AIRFLOW_ADMIN_PASSWORD:-madelinepw}"
else
  echo "Admin user already exists, skipping creation."
fi