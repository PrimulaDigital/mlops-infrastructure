# Append repo path because i cant find anything otherwise
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import contents from .env file, like sagemaker role ARN
from dotenv import load_dotenv
load_dotenv()

# Import boto3 and sagemaker for sagemaker jobs
import boto3
import sagemaker
from sagemaker.sklearn import SKLearn

# Create logs for debugging
import logging
boto3.set_stream_logger('boto3.resources', logging.DEBUG)

# Upload dataset to s3 bucket
s3 = boto3.client('s3')
bucket_name = 'test-diabetesdataset'
file_name = 'data/diabetes.csv'
s3.upload_file(file_name, bucket_name, file_name)

# Assuming the SageMaker role
sts_client = boto3.client('sts')

assumed_role_object = sts_client.assume_role(
    RoleArn=os.getenv('env_sagemakerARN'),
    RoleSessionName="SageMakerSession"
)

credentials = assumed_role_object['Credentials']

# Create a SageMaker client using the assumed role credentials
sagemaker_client = boto3.client(
    'sagemaker',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
    region_name='eu-central-1'
)

# Define the SKLearn Estimator
sklearn_estimator = SKLearn(
    entry_point='mlscripts/train.py',
    role=os.getenv('env_sagemakerARN'),
    instance_type='ml.m5.xlarge',
    framework_version='0.23-1',
    sagemaker_session=sagemaker.Session(),
    hyperparameters={'alpha': 0.001}
)

# Start the training job
sklearn_estimator.fit({'train.py': os.getenv('env_databucket')})