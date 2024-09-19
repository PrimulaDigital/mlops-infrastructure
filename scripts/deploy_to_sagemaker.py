import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from dotenv import load_dotenv
import util.s3_utils as s3_utils
import util.sagemaker_utils as sagemaker_utils
import util.model_utils as model_utils

# Load environment variables
load_dotenv()
databucket = os.getenv('env_databucket')
dataname = os.getenv('env_dataname')
outputdir = os.getenv('env_outputdir')
sagemakerARN = os.getenv('env_sagemakerARN')

local_model = '/tmp/model/'
local_data = '/tmp/data/'
os.makedirs(local_data, exist_ok=True)
joblib_model_path = os.path.join(local_model, 'model.joblib')

def main():
    # Check if data exists, upload if necessary
    if not s3_utils.data_exists_in_s3(databucket, dataname):
        s3_utils.upload_file_to_s3(dataname, databucket, dataname)
    s3_utils.download_file_from_s3(databucket, dataname, os.path.join(local_data, 'data.csv'))
    
    data = pd.read_csv(os.path.join(local_data, 'data.csv'))
    print("Data loaded successfully.")

    # Assuming the SageMaker role
    credentials = sagemaker_utils.assume_role(sagemakerARN)

    # Check if model exists, start training if not
    if not s3_utils.model_exists_in_s3(databucket, f'{outputdir}model.joblib'):
        estimator = sagemaker_utils.create_sklearn_estimator(sagemakerARN)
        model_artifacts = sagemaker_utils.start_training_job(estimator, f's3://{databucket}/{dataname}')
        print(f"Model artifacts saved at: {model_artifacts}")

        # Parse S3 path and download the model
        bucket_name, key_prefix = model_artifacts.replace('s3://', '').split('/', 1)
        local_tar_path = os.path.join(local_model, 'model.tar.gz')
        s3_utils.download_file_from_s3(bucket_name, key_prefix, local_tar_path)

        # Extract and save the model to S3
        model_utils.extract_model(local_tar_path, local_model)
        s3_utils.upload_model_to_s3(joblib_model_path, databucket, f'{outputdir}model.joblib')
        print(f"Model unpacked and saved to s3://{databucket}/{outputdir}")
    else:
        s3_utils.download_file_from_s3(databucket, f'{outputdir}model.joblib', joblib_model_path)
        model = model_utils.load_model(joblib_model_path)
        print("Model loaded successfully.")

        # Split data and evaluate model
        X = data.drop(columns=['target'])
        y = data['target']
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        y_pred = model.predict(X_test)
        print(f"Mean Squared Error: {mean_squared_error(y_true=y_test, y_pred=y_pred)}")

if __name__ == "__main__":
    main()
