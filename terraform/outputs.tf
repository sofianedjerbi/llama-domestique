output "cluster_name" {
  value = scaleway_k8s_cluster.llm.name
}

output "kubeconfig" {
  value     = scaleway_k8s_cluster.llm.kubeconfig[0].config_file
  sensitive = true
}

output "get_kubeconfig" {
  value = "scw k8s kubeconfig install ${scaleway_k8s_cluster.llm.id}"
}

output "grafana" {
  value = "kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80"
}

output "vllm" {
  value = "kubectl port-forward -n llm svc/vllm-proxy 8080:8080"
}
