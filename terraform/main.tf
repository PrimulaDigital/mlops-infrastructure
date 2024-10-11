# Set up security groups for domain. Non-restrictive for now
resource "aws_security_group" "sagemaker_sg" {
  name        = "sagemaker-sg"
  description = "Security Group for SageMaker Domain and EFS"
  vpc_id      = "${var.vpc_id}" # Replace with your VPC ID

  # Allow all ports
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

# Mount subnets to efs
resource "aws_efs_mount_target" "efs_mount" {
  for_each = toset(var.subnets)
  file_system_id = aws_efs_file_system.sagemaker_efs.id
  subnet_id = each.key
  security_groups = [aws_security_group.sagemaker_sg.id]
}
# Create the SageMaker domain
resource "aws_sagemaker_domain" "sagemaker_domain" {
  domain_name = "${var.project_name}-domain"
  auth_mode = "SSO"
  vpc_id = "${var.vpc_id}"
  subnet_ids = "${var.subnets}"
  default_user_settings {
    execution_role = aws_iam_role.sagemaker_execution_role.arn
  }
  tags = {
    Name = "${var.project_name}-domain"
  }
}

# Create domain users
# These have the same roles and security groups attached for now,
# but differ in the repositories they have access to.
resource "aws_sagemaker_user_profile" "scientist" {
  for_each = toset(var.sso_architects)  # Use a set for unique entries
  
  domain_id = aws_sagemaker_domain.sagemaker_domain.id
  user_profile_name = "${replace(replace(each.value, ".", "-"), "@", "-")}-scientist"  # Unique profile name per user
  
  # Use SSO user identifiers
  single_sign_on_user_value = each.value
  single_sign_on_user_identifier = each.value
 
  user_settings {
    execution_role = aws_iam_role.sagemaker_execution_role.arn
    security_groups = [aws_security_group.sagemaker_sg.id]
    # With lifecycles, you can trigger workflows on notebook instance creation here
    jupyter_lab_app_settings {
      code_repository {
        repository_url = "${var.studio_url}"
      }
      # This would be where you could define a docker image
      default_resource_spec {
        instance_type = var.instance_type
      }
    }
  }
}
resource "aws_sagemaker_user_profile" "architect" {
  for_each = toset(var.sso_scientists)  # Use a set for unique entries
  
  domain_id = aws_sagemaker_domain.sagemaker_domain.id
  user_profile_name = "${replace(replace(each.value, ".", "-"), "@", "-")}-architect"  # Unique profile name per user
  
  # Use SSO user identifiers
  single_sign_on_user_value = each.value
  single_sign_on_user_identifier = each.value
 
  user_settings {

    execution_role = aws_iam_role.sagemaker_execution_role.arn
    security_groups = [aws_security_group.sagemaker_sg.id]
    # With lifecycles, you can trigger workflows on notebook instance creation here
    jupyter_lab_app_settings {
      code_repository {
        repository_url = "${var.architect_url}"
      }
      # This would be where you could define a docker image
      default_resource_spec {
        instance_type = var.instance_type
      }
    }
  }
}

output "domain_efs_id" {
  value = aws_sagemaker_domain.sagemaker_domain.id
}