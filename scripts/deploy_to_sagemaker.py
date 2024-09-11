import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import boto3
import sagemaker
from sagemaker import get_execution_role
from sagemaker.sklearn import SKLearn

import mlscripts

# Upload dataset to s3 bucket
s3 = boto3.client('s3')
bucket_name = 'test-diabetesdataset'
file_name = r'data/diabetes.csv'
s3.upload_file(file_name, bucket_name, file_name)

# Assuming the SageMaker role
sts_client = boto3.client('sts')

assumed_role_object = sts_client.assume_role(
    RoleArn="arn:aws:iam::339712905337:role/service-role/AmazonSageMaker-ExecutionRole-20240910T154043",
    RoleSessionName="SageMakerSession"
)

credentials = assumed_role_object['Credentials']

# Create a SageMaker client using the assumed role credentials
sagemaker_client = boto3.client(
    'sagemaker',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
    region_name='your-region'
)

# Define the SKLearn Estimator
sklearn_estimator = SKLearn(
    entry_point='mlscripts/train.py',
    role="arn:aws:iam::339712905337:role/service-role/AmazonSageMaker-ExecutionRole-20240910T154043",
    instance_type='ml.m5.xlarge',
    framework_version='0.23-1',
    sagemaker_session=sagemaker.Session(),
    hyperparameters={'alpha': 0.001}
)

# Start the training job
sklearn_estimator.fit({'train': f's3://test-diabetesdataset/data/diabetes.csv'})