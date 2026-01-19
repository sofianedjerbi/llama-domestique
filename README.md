# llama-domestique

Un `terraform apply` et t'as un LLM qui tourne sur Kubernetes avec du GitOps

Mistral 7B sur vLLM, Flux CD, Prometheus, Grafana, GPU metrics. Le tout sur Scaleway Kapsule avec un node L4 (€0.75/h)

## Comment ça marche

Terraform crée le cluster Kapsule et bootstrap Flux CD, qui synchronise ensuite tout depuis le repo Git (GPU operator, monitoring, vLLM). Tu push une modif, Flux la déploie automatiquement

```
terraform apply
     └──► Scaleway Kapsule (+ node GPU L4)
              └──► Flux CD
                     └──► clusters/llm/apps/
                              ├── gpu-operator
                              ├── monitoring
                              └── llm (vLLM + proxy)
```

## Déployer

```bash
mise trust && mise install
cp .env.example .env
# remplis tes credentials Scaleway
source .env
cd terraform && terraform init && terraform apply
```

## Se connecter

```bash
scw k8s kubeconfig install <cluster-id>
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
terraform destroy
```

---

*Fait en une soirée pour montrer à Infomaniak que je sais déployer des LLMs sur Kubernetes avec du GitOps*
