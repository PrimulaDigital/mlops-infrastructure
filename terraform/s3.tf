# Create an S3 bucket
resource "aws_s3_bucket" "sagemaker_bucket" {
  bucket = "pd-sandbox1-sagemaker-mlops-bucket"  

  tags = {
    Name        = "SageMaker MLOps Bucket"
    Environment = "Dev"
  }
}
