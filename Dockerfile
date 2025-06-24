# Start from the AWS Lambda base image for Python 3.12
FROM public.ecr.aws/lambda/python:3.12

# Set working directory
WORKDIR /var/task

# Install system dependencies
RUN yum update -y && \
    yum install -y gcc gcc-c++ make && \
    yum clean all

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your ETL code
COPY etl/ etl/

# Create a simple test script
RUN echo 'import sys; sys.path.append("/var/task"); from etl.fetch_data import lambda_handler; print("Import successful")' > test_import.py

# Set the entry point for Lambda (pointing to a function in fetch_data.py)
CMD ["etl.fetch_data.lambda_handler"]

