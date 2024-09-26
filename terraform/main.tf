#################################################
# Variables
#################################################

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  s3_bucket_input_training_path = "${var.project_name}-training-data-${data.aws_caller_identity.current.account_id}"
  s3_bucket_output_models_path = "${var.project_name}-output-models-${data.aws_caller_identity.current.account_id}"
  s3_object_training_data = "../../data/iris.csv"
  input_training_path = "s3://${var.project_name}-training-data-${data.aws_caller_identity.current.account_id}"
  output_models_path = "s3://${var.project_name}-output-models-${data.aws_caller_identity.current.account_id}"
}

##################################################

// policy to invoke sagemaker training job, creating endpoints etc.
resource "aws_iam_policy" "sagemaker_policy" {
  name   = "${var.project_name}-sagemaker"
  policy = <<-EOF
      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Effect": "Allow",
                  "Action": [
                      "sagemaker:CreateTrainingJob",
                      "sagemaker:DescribeTrainingJob",
                      "sagemaker:StopTrainingJob",
                      "sagemaker:createModel",
                      "sagemaker:createEndpointConfig",
                      "sagemaker:createEndpoint",
                      "sagemaker:addTags"
                  ],
                  "Resource": [
                   "*"
                  ]
              },
              {
                  "Effect": "Allow",
                  "Action": [
                      "sagemaker:ListTags"
                  ],
                  "Resource": [
                   "*"
                  ]
              },
              {
                  "Effect": "Allow",
                  "Action": [
                      "iam:PassRole"
                  ],
                  "Resource": [
                   "*"
                  ],
                  "Condition": {
                      "StringEquals": {
                          "iam:PassedToService": "sagemaker.amazonaws.com"
                      }
                  }
              },
              {
                  "Effect": "Allow",
                  "Action": [
                      "events:PutTargets",
                      "events:PutRule",
                      "events:DescribeRule"
                  ],
                  "Resource": [
                  "*"
                  ]
              }
          ]
      }
EOF
}

resource "aws_iam_role_policy_attachment" "sm_invoke" {
  role       = aws_iam_role.sf_exec_role.name
  policy_arn = aws_iam_policy.sagemaker_policy.arn
}

resource "aws_iam_role_policy_attachment" "cloud_watch_full_access" {
  role       = aws_iam_role.sf_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

#################################################
# IAM Roles and Policies for SageMaker
#################################################

// IAM role for SageMaker training job
data "aws_iam_policy_document" "sagemaker_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["sagemaker.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "sagemaker_exec_role" {
  name               = "${var.project_name}-sagemaker-exec"
  assume_role_policy = data.aws_iam_policy_document.sagemaker_assume_role.json
}

// Policies for sagemaker execution training job
resource "aws_iam_policy" "sagemaker_s3_policy" {
  name   = "${var.project_name}-sagemaker-s3-policy"
  policy = <<-EOF
      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Effect": "Allow",
                  "Action": [
                      "s3:*"
                  ],
                  "Resource": [
                   "${aws_s3_bucket.bucket_training_data.arn}",
                   "${aws_s3_bucket.bucket_output_models.arn}",
                   "${aws_s3_bucket.bucket_training_data.arn}/*",
                   "${aws_s3_bucket.bucket_output_models.arn}/*"
                  ]
              }
          ]
      }
EOF
}

resource "aws_iam_role_policy_attachment" "s3_restricted_access" {
  role       = aws_iam_role.sagemaker_exec_role.name
  policy_arn = aws_iam_policy.sagemaker_s3_policy.arn
}

resource "aws_iam_role_policy_attachment" "sagemaker_full_access" {
  role       = aws_iam_role.sagemaker_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

#################################################
# ECR Repository
#################################################

resource "aws_ecr_repository" "ecr_repository" {
  name                 = var.project_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

#################################################
# S3 Buckets
#################################################
resource "aws_s3_bucket" "bucket_training_data" {
  bucket = local.s3_bucket_input_training_path
}

resource "aws_s3_bucket_acl" "bucket_training_data_acl" {
  bucket = aws_s3_bucket.bucket_training_data.id
  acl    = "private"
  depends_on = [aws_s3_bucket_ownership_controls.s3_training_bucket_acl_ownership]
}

# Resource to avoid error "AccessControlListNotSupported: The bucket does not allow ACLs"
resource "aws_s3_bucket_ownership_controls" "s3_training_bucket_acl_ownership" {
  bucket = aws_s3_bucket.bucket_training_data.id
  rule {
    object_ownership = "ObjectWriter"
  }
}
resource "aws_s3_object" "object" {
  bucket = aws_s3_bucket.bucket_training_data.id
  key    = "iris.csv"
  source = local.s3_object_training_data
}

resource "aws_s3_bucket" "bucket_output_models" {
  bucket = local.s3_bucket_output_models_path
}

resource "aws_s3_bucket_acl" "bucket_output_models_acl" {
  bucket = aws_s3_bucket.bucket_output_models.id
  acl    = "private"
  depends_on = [aws_s3_bucket_ownership_controls.s3_bucket_acl_ownership]
}

# Resource to avoid error "AccessControlListNotSupported: The bucket does not allow ACLs"
resource "aws_s3_bucket_ownership_controls" "s3_bucket_acl_ownership" {
  bucket = aws_s3_bucket.bucket_output_models.id
  rule {
    object_ownership = "ObjectWriter"
  }
}

#################################################
# Outputs
#################################################

output "ecr_repository_url" {
  value = aws_ecr_repository.ecr_repository.repository_url
  description = "ECR URL for the Docker Image"
}