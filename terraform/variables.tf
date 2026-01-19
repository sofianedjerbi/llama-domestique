variable "region" {
  type    = string
  default = "fr-par"
}

variable "zone" {
  type    = string
  default = "fr-par-1"
}

variable "cluster_name" {
  type    = string
  default = "llm"
}

variable "gpu_instance_type" {
  type    = string
  default = "L4-1-24G"
}

variable "gpu_node_count" {
  type    = number
  default = 1
}

variable "github_owner" {
  type    = string
  default = "sofianedjerbi"
}

variable "github_repository" {
  type    = string
  default = "llama-domestique"
}
