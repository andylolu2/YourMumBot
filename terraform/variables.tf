variable "tag" {
  description = "Tag name"
  type        = string
}

variable "aws_region" {
  description = "The region for the aws resources"
  type        = string
}

variable "aws_local_zone" {
  description = "The local zone for the aws resources. This must match aws_region"
  type        = string
}

variable "ec2_instance_type" {
  description = "The instance type for the ec2 instance"
  type        = string
}
