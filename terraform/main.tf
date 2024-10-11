# Set up security groups for domain. Non-restrictive for now
resource "aws_security_group" "sagemaker_sg" {
  name        = "sagemaker-sg"
  description = "Security Group for SageMaker Domain and EFS"
  vpc_id      = "${var.vpc_id}" # Replace with your VPC ID

  ingress {
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "sagemaker-sg"
  }
}

# Set up Elastic File Storage for domain
resource "aws_efs_file_system" "sagemaker_efs" {
  creation_token = "${var.project_name}-efs"
  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  tags = {
    Name = "sagemaker-efs"
  }
}

resource "aws_efs_mount_target" "efs_mount" {
  for_each = toset(var.subnets)
  file_system_id = aws_efs_file_system.sagemaker_efs.id
  subnet_id = each.key
  security_groups = [aws_security_group.sagemaker_sg.id]
}


# Create the SageMaker domain
resource "aws_sagemaker_domain" "sagemaker_domain" {
  domain_name = "${var.project_name}-domain"
  auth_mode = "IAM"
  vpc_id = "${var.vpc_id}"
  subnet_ids = "${var.subnets}"
  default_user_settings {
    execution_role = aws_iam_role.sagemaker_execution_role.arn
    security_groups = [aws_security_group.sagemaker_sg.id]
  }
  tags = {
    Name = "${var.project_name}-domain"
  }
}

output "domain_efs_id" {
  value = aws_sagemaker_domain.sagemaker_domain.id
}