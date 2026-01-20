variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "llm"
}

variable "domain" {
  description = "Root domain name"
  type        = string
  default     = "sofianedjerbi.com"
}

variable "subdomain" {
  description = "Subdomain for the LLM endpoint"
  type        = string
  default     = "infomaniak"
}
