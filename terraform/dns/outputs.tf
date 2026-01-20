output "fqdn" {
  description = "Fully qualified domain name for the LLM endpoint"
  value       = aws_route53_record.llm.fqdn
}

output "lb_hostname" {
  description = "Load balancer hostname"
  value       = data.kubernetes_service.ingress.status[0].load_balancer[0].ingress[0].hostname
}
