#################################################
# Variables
#################################################

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  s3_bucket_input_training_path = "${var.project_name}-training-data-${data.aws_caller_identity.current.account_id}"
  s3_bucket_output_models_path = "${var.project_name}-output-models-${data.aws_caller_identity.current.account_id}"
  s3_object_training_data = "../data/iris.csv"
  s3_object_train_script = "../ml-scripts/train.py"
  input_training_path = "s3://${var.project_name}-training-data-${data.aws_caller_identity.current.account_id}"
  output_models_path = "s3://${var.project_name}-output-models-${data.aws_caller_identity.current.account_id}"
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
# Step function role
#################################################

// IAM role for Step Functions state machine
data "aws_iam_policy_document" "sf_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["states.${data.aws_region.current.name}.amazonaws.com"]
    }
  }
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "sf_exec_role" {
  name               = "${var.project_name}-sfn-exec"
  assume_role_policy = data.aws_iam_policy_document.sf_assume_role.json
}

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
# S3 Buckets & ECR
#################################################

resource "aws_s3_bucket" "bucket_training_data" {
  bucket = local.s3_bucket_input_training_path
}

 // Upload training data to bucket
 resource "aws_s3_object" "data_object" {
   bucket = aws_s3_bucket.bucket_training_data.id
   key    = "iris.csv"
   source = local.s3_object_training_data
 }

# // Upload train.py to bucket
# resource "aws_s3_object" "train_object" {
#   bucket = aws_s3_bucket.bucket_training_data.id
#   key    = "train.py"
#   source = local.s3_object_train_script
# }

resource "aws_s3_bucket" "bucket_output_models" {
  bucket = local.s3_bucket_output_models_path
}

# Create an ECR repository
resource "aws_ecr_repository" "ecr_repo" {
  name                 = "${var.project_name}-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

#################################################
# Sagemaker Training job
#################################################

resource "aws_sfn_state_machine" "sagemaker_training_job" {
  name     = "step-machine-training"
  role_arn = aws_iam_role.sf_exec_role.arn

  definition = jsonencode({
    Comment = "A Step Function that creates a SageMaker training job",
    StartAt = "StartTrainingJob",
    States = {
      StartTrainingJob = {
        Type = "Task",
        Resource = "arn:aws:states:::sagemaker:createTrainingJob.sync",
        Parameters = {
          TrainingJobName = "iris-training4",
          AlgorithmSpecification = {
            TrainingImage = "${aws_ecr_repository.ecr_repo.repository_url}",
            TrainingInputMode = "File"
          },
          RoleArn = "${aws_iam_role.sagemaker_exec_role.arn}",
          InputDataConfig = [
            {
              ChannelName = "train",
              DataSource = {
                S3DataSource = {
                  S3DataType = "S3Prefix",
                  S3Uri = local.input_training_path,
                  S3DataDistributionType = "FullyReplicated"
                }
              }
            }
          ],
          OutputDataConfig = {
            S3OutputPath = local.output_models_path
          },
          ResourceConfig = {
            InstanceType     = var.training_instance_type,
            InstanceCount    = 1,
            VolumeSizeInGB   = var.volume_size_sagemaker
          },
          StoppingCondition = {
            MaxRuntimeInSeconds = 3600
          },
          HyperParameters = {
            "test" = "test"
          }
        },
        End = true
      }
    }
  })
}

output "ecr_repository_url" {
  value = aws_ecr_repository.ecr_repo.repository_url
  description = "ECR URL for the Docker Image"
}