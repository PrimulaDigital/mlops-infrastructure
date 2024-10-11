# main.py
from scripts import deploy_to_sagemaker
from scripts import prepare_data

def main():
    print("Main Script: Please choose an option:")
    print("1. Deploy to SageMaker")
    print("2. Prepare Data")
    
    choice = input("Enter your choice (1/2): ").strip()
    
    if choice == '1':
        deploy_to_sagemaker.main()
    elif choice == '2':
        prepare_data.main()
    else:
        print("Invalid choice. Please select 1 or 2.")

if __name__ == "__main__":
    main()