output "cluster_name" {
  value = module.eks.cluster_name
}

output "kubeconfig" {
  value = "aws eks update-kubeconfig --region ${var.region} --name ${module.eks.cluster_name}"
}

output "grafana" {
  value = "kubectl port-forward -n monitoring svc/kube-prometheus-grafana 3000:80"
}

output "vllm" {
  value = "kubectl port-forward -n llm svc/vllm 8000:8000"
}
