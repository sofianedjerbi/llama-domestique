# llama-domestique

Un `terraform apply` et t'as un LLM qui tourne sur EKS avec du monitoring GPU

Mistral 7B sur vLLM, Prometheus, Grafana, node g4dn.xlarge ($360/mois si tu laisses tourner h24, merci Jeff)

## Déployer

```bash
cd terraform
terraform init
terraform apply
```

15min, va te faire un café

## Se connecter

```bash
aws eks update-kubeconfig --region eu-west-1 --name llm
kubectl port-forward -n llm svc/vllm 8000:8000
kubectl port-forward -n monitoring svc/kube-prometheus-grafana 3000:80
```

Grafana: admin/admin (oui c'est en clair, tu peux rajouter SOPS si ça te choque)

## Tester

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistralai/Mistral-7B-Instruct-v0.3",
    "messages": [{"role": "user", "content": "Salut!"}]
  }'
```

## Changer de modèle

Dans `helm/vllm/values.yaml`, pour les modèles gated ajoute `hfToken`

## Nettoyer

```bash
terraform destroy
```

Oublie pas sinon tu vas pleurer à la fin du mois!

---

*Fait en une soirée pour montrer à Infomaniak que je sais déployer des LLMs sur Kubernetes*
