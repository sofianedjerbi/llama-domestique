terraform {
  required_version = ">= 1.0"
  required_providers {
    scaleway = {
      source  = "scaleway/scaleway"
      version = "~> 2.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    flux = {
      source  = "fluxcd/flux"
      version = "~> 1.0"
    }
  }
}

provider "scaleway" {
  region = var.region
  zone   = var.zone
}

resource "scaleway_k8s_cluster" "llm" {
  name    = var.cluster_name
  version = "1.29"
  cni     = "cilium"

  delete_additional_resources = true

  autoscaler_config {
    disable_scale_down = true
  }
}

resource "scaleway_k8s_pool" "gpu" {
  cluster_id  = scaleway_k8s_cluster.llm.id
  name        = "gpu"
  node_type   = var.gpu_instance_type
  size        = var.gpu_node_count
  autohealing = true

  upgrade_policy {
    max_unavailable = 1
  }
}

resource "null_resource" "wait_for_cluster" {
  depends_on = [scaleway_k8s_pool.gpu]

  provisioner "local-exec" {
    command = "sleep 30"
  }
}

provider "kubernetes" {
  host                   = scaleway_k8s_cluster.llm.kubeconfig[0].host
  token                  = scaleway_k8s_cluster.llm.kubeconfig[0].token
  cluster_ca_certificate = base64decode(scaleway_k8s_cluster.llm.kubeconfig[0].cluster_ca_certificate)
}

provider "flux" {
  kubernetes = {
    host                   = scaleway_k8s_cluster.llm.kubeconfig[0].host
    token                  = scaleway_k8s_cluster.llm.kubeconfig[0].token
    cluster_ca_certificate = base64decode(scaleway_k8s_cluster.llm.kubeconfig[0].cluster_ca_certificate)
  }
  git = {
    url = "https://github.com/${var.github_owner}/${var.github_repository}.git"
  }
}

resource "flux_bootstrap_git" "this" {
  depends_on = [null_resource.wait_for_cluster]

  path = "clusters/${var.cluster_name}"
}
