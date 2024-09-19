import boto3

s3 = boto3.client('s3')

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

def upload_file_to_s3(local_path, bucket_name, s3_path):
    try:
        s3.upload_file(local_path, bucket_name, s3_path)
        print(f"File {local_path} uploaded to s3://{bucket_name}/{s3_path}")
    except Exception as e:
        print(f"Failed to upload {local_path} to S3: {e}")

def upload_model_to_s3(local_path, bucket_name, s3_path):
    try:
        s3.upload_file(local_path, bucket_name, s3_path)
        print(f"Model {local_path} uploaded to s3://{bucket_name}/{s3_path}")
    except Exception as e:
        print(f"Failed to upload {local_path} to S3: {e}")

def download_file_from_s3(bucket_name, s3_key, local_path):
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        print(f"File {s3_key} downloaded to {local_path}")
    except Exception as e:
        print(f"Failed to download {s3_key}: {e}")
