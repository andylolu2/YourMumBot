variable "do_token" {
  description = "Digital ocean personal access token. Provided as workspace variable on terraform cloud."
  type        = string
}

variable "tag" {
  description = "Tag name"
  type        = string
}

variable "app_size" {
  description = "The instance type for the droplet. Can be found at https://slugs.do-api.dev/."
  type        = string
}

variable "region" {
  description = "The region for the resources. Can be found at https://slugs.do-api.dev/."
  type        = string
}
