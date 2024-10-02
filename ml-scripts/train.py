import argparse
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

def load_data(data_path):
    df = pd.read_csv(data_path)
    X = df.drop('species', axis=1)
    y = df['species']
    return X, y

def train_model(X, y):
    model = RandomForestClassifier()
    model.fit(X, y)
    return model

if __name__ == '__main__':
    data_path = '/opt/ml/input/data/train/'
    print("Files in the directory:", os.listdir(data_path))
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='/opt/ml/input/data/train/iris.csv')
    args = parser.parse_args()

    # Load the data
    X, y = load_data(args.data)

    # Train the model
    model = train_model(X, y)

    # Save the model
    model_path = os.path.join('/opt/ml/model', 'model.joblib')
    joblib.dump(model, model_path)
