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