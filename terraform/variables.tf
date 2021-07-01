variable "tag" {
  description = "Tag name"
  type        = string
  default     = "YourMumBot"
}

variable "aws_region" {
  description = "The region for the aws resources"
  type        = string
  default     = "ap-northeast-2"
}

variable "aws_local_zone" {
  description = "The local zone for the aws resources. This must match aws_region"
  type        = string
  default     = "ap-northeast-2a"
}

variable "ec2_instance_type" {
  description = "The instance type for the ec2 instance"
  type        = string
  default     = "t3a.nano"
}
