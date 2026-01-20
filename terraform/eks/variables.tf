variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "cluster_name" {
  type    = string
  default = "llm"
}

variable "gpu_instance_type" {
  type    = string
  default = "g4dn.xlarge"
}

variable "gpu_node_count" {
  type    = number
  default = 1
}
