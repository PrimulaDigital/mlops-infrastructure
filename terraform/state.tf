terraform {
  backend "s3" {
    region  = "eu-central-1"
    encrypt = true
    bucket = "pd-sandbox01-st-tf-dev-feature-create-endpoint"
    key = "dev/mlops-infrastructure/terraform.tfstate"
  }
}