variable "aws_region" {
  type        = string
  description = "AWS region to use for resources."
  default     = "eu-central-1"
}

variable "project_name" {
  type = string
  description = "Name of our project used in naming resources"
  default = "pd-sandbox01"
}

variable "vpc_id" {
  type = string
  description = "ID of pre built VPC"
  default = "vpc-0276724cceddf86eb"
}
 
 variable "subnets" {
  type = list
  description = "List of available subnets in the pre built VPC"
  default = ["subnet-073537da5ee37885a","subnet-07663b1b22ffaee50","subnet-00944e1eab3a4f1b4"]
 }

 variable "instance_type" {
  type = string
  description = "Instance type for sagemaker jobs"
  default = "ml.t3.medium"
 }