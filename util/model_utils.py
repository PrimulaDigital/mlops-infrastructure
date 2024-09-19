import tarfile
import joblib
import os

def extract_model(tar_path, extract_to):
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=extract_to)

def load_model(model_path):
    return joblib.load(model_path)

def save_model_to_s3(model_path, bucket, key):
    with open(model_path, 'rb') as f:
        s3.upload_fileobj(f, bucket, key)
    print(f"Model saved to s3://{bucket}/{key}")
