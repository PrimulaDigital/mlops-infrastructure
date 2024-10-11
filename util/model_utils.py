import tarfile
import joblib

def extract_model(tar_path, extract_to):
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=extract_to)

def load_model(model_path):
    return joblib.load(model_path)