from data.Diabetes import load_data
import pandas as pd

def main():
    '''
    Load Diabetes Dataset. Create .csv file and return it.
    '''
    diabetes = load_data()

    df = pd.DataFrame(data=diabetes.data, columns=diabetes.feature_names)
    df['target'] = diabetes.target

    return df.to_csv('data/diabetes.csv', index=False)

if __name__ == "__main__":
    main()