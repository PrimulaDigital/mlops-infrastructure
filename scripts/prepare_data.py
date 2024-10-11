from sklearn.datasets import load_diabetes
import pandas as pd
import os

def main():
    '''
    Load Diabetes Dataset. Create .csv file and return it.
    '''
    diabetes = load_diabetes()

    df = pd.DataFrame(data=diabetes.data, columns=diabetes.feature_names)
    df['target'] = diabetes.target

    temp_dir = '/tmp/data'
    os.makedirs(temp_dir, exist_ok=True)

    csv_file_path = os.path.join(temp_dir, 'data.csv')
    df.to_csv(csv_file_path, index=False)
    print(f'data.csv save to {csv_file_path}')

if __name__ == "__main__":
    main()