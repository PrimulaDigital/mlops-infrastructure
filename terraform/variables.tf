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
}
 
 variable "subnets" {
  type = list
  description = "List of available subnets in the pre built VPC"
}

 variable "instance_type" {
  type = string
  description = "Instance type for sagemaker jobs"
  default = "ml.t3.large"
 }

 variable "architect_url" {
  type = string
  description = "URL for git repository that builds the infrastructure etc."
 }

 variable "studio_url" {
  type = string
  description = "URL for git repositroy that focuses on providing automation to data scientists"
 }

 variable "sso_architects" {
  type = list
  description = "List of SSO users that are architects"
 }

 variable "sso_scientists" {
  type = list
  description = "List of SSO users that are data scientists"
 }