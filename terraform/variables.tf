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
 