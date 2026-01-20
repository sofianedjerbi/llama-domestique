variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "cluster_name" {
  type    = string
  default = "llm"
}

variable "github_owner" {
  type    = string
  default = "sofianedjerbi"
}

variable "github_repository" {
  type    = string
  default = "llama-domestique"
}

variable "github_token" {
  type      = string
  sensitive = true
}
