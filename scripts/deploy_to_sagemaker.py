# Append repo path because i cant find anything otherwise
import sys
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import contents from .env file, like sagemaker role ARN
from dotenv import load_dotenv
load_dotenv()

# Set environment variables
databucket = os.getenv('env_databucket')
dataname = os.getenv('env_dataname')
outputdir = os.getenv('env_outputdir')
sagemakerARN = os.getenv('env_sagemakerARN')

# Import boto3 and sagemaker for sagemaker jobs
import boto3
import sagemaker
from sagemaker.sklearn import SKLearn

# Create logs for debugging
import logging
boto3.set_stream_logger('boto3.resources', logging.DEBUG)

# Dependancies for model unpacking and storing
import tarfile
import joblib

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Create s3 and sts client
s3 = boto3.client('s3')
sts_client = boto3.client('sts')
local_model = '/tmp/model/'
local_data = '/tmp/data/'

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
# Load the data
s3.download_file(databucket, dataname, os.path.join(local_data, 'diabetes.csv'))
data = pd.read_csv(os.path.join(local_data, 'diabetes.csv'))
print("Data loaded successfully.")

# Assuming the SageMaker role
assumed_role_object = sts_client.assume_role(
    RoleArn = sagemakerARN,
    RoleSessionName = "SageMakerSession"
)

# Set credentials dictionary
credentials = assumed_role_object['Credentials']

# Assuming .joblib file is extracted inside local_dir
joblib_model_path = os.path.join(local_model, 'model.joblib')

if(not model_exists_in_s3(databucket, f'{outputdir}model.joblib'  )):
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
    sklearn_estimator.fit({'train': f's3://{databucket}/{dataname}'})

    # Get the S3 path of the model artifacts after training completes
    model_artifacts = sklearn_estimator.model_data
    print(f"Model artifacts saved at: {model_artifacts}")

    # Parse the S3 bucket and key from the model artifacts URL
    bucket_name, key_prefix = model_artifacts.replace('s3://', '').split('/', 1)

    # Local paths
    local_dir = '/tmp/model/'
    local_tar_path = os.path.join(local_dir, 'model.tar.gz')

    # Create local directory if not exists
    os.makedirs(local_dir, exist_ok=True)

    # Download the model artifact (model.tar.gz) from S3
    s3.download_file(bucket_name, key_prefix, local_tar_path)

    # Extract the model.tar.gz
    with tarfile.open(local_tar_path, 'r:gz') as tar:
        tar.extractall(path=local_dir)

    # Assuming .joblib file is extracted inside local_dir
    joblib_model_path = os.path.join(local_dir, 'model.joblib')

    # Save model to bucket
    with open(joblib_model_path, 'rb') as f:
        s3.upload_fileobj(f, databucket, f'{outputdir}model.joblib')

    print(f"Model unpacked and saved to s3://{databucket}/{outputdir}")
else:
    s3.download_file(databucket, f'{outputdir}model.joblib', os.path.join(local_model, 'diabetes.csv'))
    # Load the model
    model = joblib.load(joblib_model_path)
    print("Model loaded successfully.")

    X = data.drop(columns=['target'])
    y = data['target']
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    y_pred = model.predict(X_test)
    print(mean_squared_error(y_true = y_test, y_pred = y_pred))