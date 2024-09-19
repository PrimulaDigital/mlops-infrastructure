terraform {
  backend "s3" {
    region  = "eu-central-1"
    encrypt = true
    bucket = "pd-st-tf-dev"
    key = "dev/mlops-infrastructure/terraform.tfstate"
  }
}
