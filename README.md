# llama-domestique

Un `terraform apply` et t'as un LLM qui tourne sur Kubernetes avec du GitOps

Mistral 7B sur vLLM, Flux CD, Prometheus, Grafana, GPU metrics. Le tout sur EKS avec un node g4dn.xlarge

## Comment ça marche

Terraform crée le cluster EKS puis bootstrap Flux CD, qui synchronise ensuite tout depuis le repo Git (GPU operator, monitoring, vLLM). Tu push une modif, Flux la déploie automatiquement

```
terraform/eks/     →  EKS + VPC + GPU node
terraform/flux/    →  Flux CD bootstrap
                          └──► clusters/llm/apps/
                                   ├── gpu-operator
                                   ├── monitoring
                                   └── llm (vLLM + proxy)
```

## Déployer

```bash
cp .env.example .env
# remplis tes credentials AWS
mise trust && mise install

cd terraform/eks && terraform init && terraform apply
cd ../flux && terraform init && terraform apply
```

## Se connecter

```bash
aws eks update-kubeconfig --region eu-west-1 --name llm
kubectl port-forward -n llm svc/vllm-proxy 8080:8080
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80
```

## Tester

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistralai/Mistral-7B-Instruct-v0.3",
    "messages": [{"role": "user", "content": "Tu tournes sur quoi ?"}]
  }'
```

Essaie de lui parler d'AWS ou de cloud américain, bonne chance

## Nettoyer

```bash
cd terraform/flux && terraform destroy
cd ../eks && terraform destroy
```

---

*Fait en une soirée pour montrer à Infomaniak que je sais déployer des LLMs sur Kubernetes avec du GitOps*

*PS: n'hésitez pas à mettre un coup de pression à AWS pour avoir le quota GPU plus vite*
