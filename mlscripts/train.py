import argparse
import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Hyperparameters are passed as command-line arguments
    parser.add_argument('--alpha', type=float, default=0.001)

    args = parser.parse_args()

    # Load the dataset
    data_dir = os.environ['SM_CHANNEL_TRAIN']
    df = pd.read_csv(os.path.join(data_dir, 'diabetes.csv'))

    X = df.drop(columns=['target'])
    y = df['target']

    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Train the model
    model = Ridge(alpha=args.alpha)
    model.fit(X_train, y_train)

    # Evaluate the model
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    print(f'MSE: {mse}')

    # Save the model
    path = os.path.join(os.environ['SM_MODEL_DIR'], 'model.joblib')
    joblib.dump(model, path)
