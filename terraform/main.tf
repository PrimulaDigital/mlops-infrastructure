# Create the SageMaker domain
resource "aws_sagemaker_domain" "example" {
  vpc_id = "vpc-0276724cceddf86eb"
  subnet_ids = ["subnet-073537da5ee37885a","subnet-07663b1b22ffaee50","subnet-00944e1eab3a4f1b4"]
  domain_name = "${var.project_name}-domain"
  auth_mode = "IAM"
  default_user_settings {
    execution_role = aws_iam_role.sagemaker_execution_role.arn
  }
}