import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.Diabetes import load_data
import pandas as pd

def getCsv():
    # Load the diabetes dataset
    diabetes = load_data()

    # Create a DataFrame
    df = pd.DataFrame(data=diabetes.data, columns=diabetes.feature_names)
    df['target'] = diabetes.target

    # Save the dataset as a CSV file and return it
    return df.to_csv('data/diabetes.csv', index=False)