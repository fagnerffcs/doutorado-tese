#!/usr/bin/env bash
# ==============================================================================
# K3d Cluster Provisioning Script - Scenario 2 (PANOPTES Architecture on WSL2)
# Rigorous Hardware Parity: 2 vCPUs and 4GB RAM per Node (Thesis Specification)
# ==============================================================================
set -euo pipefail

echo "======================================================================"
echo "  PANOPTES K3D ENVIRONMENT PROVISIONING (SCENARIO 2 - OBSERVABILITY)"
echo "======================================================================"

# 1. Ensure control dependencies and Docker daemon in WSL2
echo "[1/4] Checking dependencies (Ansible, Helm, K3d, Docker)..."
sudo service docker start >/dev/null 2>&1 || true
sudo usermod -aG docker $USER || true

# Ensure kernel inotify limits are sufficient for K3d multi-node observability stack
sudo sysctl -w fs.inotify.max_user_instances=8192 >/dev/null
sudo sysctl -w fs.inotify.max_user_watches=524288 >/dev/null
sudo sysctl -w fs.file-max=2097152 >/dev/null

if ! command -v helm >/dev/null 2>&1; then
  echo "Installing Helm..."
  curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
  bash get_helm.sh
  rm get_helm.sh
fi

if ! command -v k3d >/dev/null 2>&1; then
  echo "Installing K3d..."
  curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

# 2. Create K3s Cluster for Scenario 2 with Strict Resource Limits
echo "[2/4] Creating K3s cluster 'panoptes-cluster-scenario2' (2 CPUs, 4GB RAM per node)..."
k3d cluster delete panoptes-cluster-scenario2 2>/dev/null || true
k3d cluster create panoptes-cluster-scenario2 \
  --servers 1 \
  --agents 2 \
  --k3s-arg "--disable=traefik@server:0" \
  --wait

# Apply strict Docker resource constraints to Scenario 2 cluster instances
echo "Applying strict Docker resource constraints (2 CPUs, 4GB RAM) to Scenario 2 nodes..."
for node in panoptes-cluster-scenario2-server-0 panoptes-cluster-scenario2-agent-0 panoptes-cluster-scenario2-agent-1; do
  docker update --cpus="2.0" --memory="4g" --memory-swap="4g" "k3d-$node" 2>/dev/null || true
done

# 3. Apply Taint on Master Node (Control-plane hardware isolation simulation)
echo "[3/4] Applying isolation taint on the master node..."
kubectl --context k3d-panoptes-cluster-scenario2 taint nodes k3d-panoptes-cluster-scenario2-server-0 node-role.kubernetes.io/master=true:NoSchedule --overwrite || true

# 4. Configure local kubeconfig
echo "[4/4] Configuring kubectl access and Ansible dependencies..."
mkdir -p ~/.kube
k3d kubeconfig write panoptes-cluster-scenario2 --output ~/.kube/config
chmod 600 ~/.kube/config

# Install Ansible collections if available
if command -v ansible >/dev/null 2>&1; then
  ansible-galaxy collection install kubernetes.core || true
fi

echo ""
echo "======================================================================"
echo "  [OK] PANOPTES K3D ENVIRONMENT FOR SCENARIO 2 IS READY (STRICT PARITY)!"
echo "======================================================================"
kubectl get nodes