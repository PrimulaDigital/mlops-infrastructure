variable "project_name" {
  type = string
}

variable "region" {
  type    = string
}

variable "training_instance_type" {
  type = string
}

variable "inference_instance_type" {
  type = string
}

variable "volume_size_sagemaker" {
  type = number
}

variable s3_bucket_input_training_path {
  type = string
  description = "S3 path where training data is stored"
}

variable s3_bucket_output_models_path {
  type = string
  description = "S3 path were the output (trained models etc.) will be stored"
}

variable s3_object_training_data {
  type = string
  description = "S3 path where training data is stored"
}

variable "runtime" {
  type = string
  default = "python3.9.19"
}

variable "memory_size" {
  type = string
  default = "128"
}

variable "timeout" {
  type = string
  default = "200"
}