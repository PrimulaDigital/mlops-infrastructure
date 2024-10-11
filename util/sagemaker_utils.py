import boto3
from sagemaker.sklearn import SKLearn
import sagemaker

def assume_role(sagemakerARN):
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn=sagemakerARN,
        RoleSessionName="SageMakerSession"
    )
    return assumed_role_object['Credentials']

def create_sklearn_estimator(role_arn, instance_type='ml.m5.large', hyperparameters={'alpha': 0.001}):
    sklearn_estimator = SKLearn(
        entry_point='mlscripts/train.py',
        role=role_arn,
        instance_type=instance_type,
        framework_version='0.23-1',
        sagemaker_session=sagemaker.Session(),
        hyperparameters=hyperparameters
    )
    return sklearn_estimator

def start_training_job(estimator, s3_input_path):
    estimator.fit({'train': s3_input_path})
    return estimator.model_data
