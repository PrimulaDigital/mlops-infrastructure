# Append repo path because i cant find anything otherwise
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import contents from .env file, like sagemaker role ARN
from dotenv import load_dotenv
load_dotenv()

# Set environment variables
databucket = os.getenv('env_databucket')
dataname = os.getenv('env_dataname')
modelname = os.getenv('env_modelname')
sagemakerARN = os.getenv('env_sagemakerARN')

# Import boto3 and sagemaker for sagemaker jobs
import boto3
import sagemaker
from sagemaker.sklearn import SKLearn

# Create logs for debugging
import logging
boto3.set_stream_logger('boto3.resources', logging.DEBUG)

import joblib

# Create s3 and sts client
s3 = boto3.client('s3')
sts_client = boto3.client('sts')

def model_exists_in_s3(bucket_name, model_file_name):
    try:
        s3.head_object(Bucket=bucket_name, Key=model_file_name)
        print(f"Model {model_file_name} exists in S3 bucket {bucket_name}")
        return True
    except Exception as e:
        print(f"Model {model_file_name} does not exist: {e}")
        return False
    
def data_exists_in_s3(bucket_name, data_file_name):
    try:
        s3.head_object(Bucket=bucket_name, Key=data_file_name)
        print(f"Data {data_file_name} exists in S3 bucket {bucket_name}")
        return True
    except Exception as e:
        print(f"Data {data_file_name} does not exist: {e}")
        return False

# Check if data already exists in bucket
if(not data_exists_in_s3(databucket, dataname)):
    # Upload dataset to s3 bucket
    s3.upload_file(dataname, databucket, dataname)

# Assuming the SageMaker role
assumed_role_object = sts_client.assume_role(
    RoleArn = sagemakerARN,
    RoleSessionName = "SageMakerSession"
)

# Set credentials dictionary
credentials = assumed_role_object['Credentials']

# Create a SageMaker client using the assumed role credentials
sagemaker_client = boto3.client(
    'sagemaker',
    aws_access_key_id = credentials['AccessKeyId'],
    aws_secret_access_key = credentials['SecretAccessKey'],
    aws_session_token = credentials['SessionToken'],
    region_name = 'eu-central-1'
)

# Define the SKLearn Estimator
sklearn_estimator = SKLearn(
    entry_point = 'mlscripts/train.py',
    role = sagemakerARN,
    instance_type = 'ml.m5.xlarge',
    framework_version = '0.23-1',
    sagemaker_session = sagemaker.Session(),
    hyperparameters = {'alpha': 0.001}
)

# Start the training job
sklearn_estimator.fit({'train': f's3://{databucket}'})