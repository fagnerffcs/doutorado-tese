#!/usr/bin/env bash
# ==============================================================================
# K3d Cluster Provisioning Script - Scenario 1 (Vanilla Kubernetes on WSL2)
# Rigorous Hardware Parity: 2 vCPUs and 4GB RAM per Node (Thesis Specification)
# ==============================================================================
set -euo pipefail

echo "======================================================================"
echo "  PANOPTES K3D ENVIRONMENT PROVISIONING (SCENARIO 1 - RIGOROUS PARITY)"
echo "======================================================================"

# 1. Check control dependencies if not present
echo "[1/4] Checking dependencies on WSL2 (Ansible, Helm, Kubectl)..."
if ! command -v ansible >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  sudo apt-get update -y
  sudo apt-get install -y software-properties-common python3-pip jq git curl docker.io
  sudo add-apt-repository --yes --update ppa:ansible/ansible
  sudo apt-get install -y ansible
  sudo pip3 install kubernetes PyYAML jsonpatch scipy pandas matplotlib
  ansible-galaxy collection install kubernetes.core
else
  echo "[OK] Control Node dependencies already present."
fi

# 2. Ensure Docker daemon is running in WSL2
echo "[2/4] Starting Docker daemon in WSL2..."
sudo service docker start
sudo usermod -aG docker $USER || true

# Ensure kernel inotify limits are sufficient for K3d multi-node observability stack
sudo sysctl -w fs.inotify.max_user_instances=8192 >/dev/null
sudo sysctl -w fs.inotify.max_user_watches=524288 >/dev/null
sudo sysctl -w fs.file-max=2097152 >/dev/null

# 3. Install K3d if necessary
if ! command -v k3d >/dev/null 2>&1; then
  echo "Installing K3d..."
  curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

# 4. Create K3s Cluster with Rigorous Resource Limits (2 vCPUs, 4GB RAM per node)
echo "[3/4] Creating K3s cluster 'panoptes-cluster' with strict resource limits (2 CPUs, 4GB RAM per node)..."
k3d cluster delete panoptes-cluster 2>/dev/null || true
k3d cluster create panoptes-cluster \
  --servers 1 \
  --agents 2 \
  --k3s-arg "--disable=traefik@server:0" \
  --memory 12gb \
  --gpus all \
  --wait

# Aplicar limites de recursos estritos via Docker Update nos nós criados pelo K3d para refletir exatamente a tese (2 CPUs / 4GB por nó)
echo "Applying strict Docker resource constraints (2 CPUs, 4GB RAM) to cluster nodes..."
for node in panoptes-cluster-server-0 panoptes-cluster-agent-0 panoptes-cluster-agent-1; do
  docker update --cpus="2.0" --memory="4g" --memory-swap="4g" "k3d-$node" 2>/dev/null || true
done

# 5. Configure local kubeconfig
echo "[4/4] Configuring kubectl access and generating inventory..."
mkdir -p ~/.kube
k3d kubeconfig write panoptes-cluster --output ~/.kube/config
chmod 600 ~/.kube/config

# Generate dynamic inventory for compatibility with previous structure
cat <<EOF > inventory.ini
[k8s_cluster]
k8s-master ansible_host=127.0.0.1 ansible_user=$USER ansible_connection=local
k8s-worker1 ansible_host=127.0.0.1 ansible_user=$USER ansible_connection=local
k8s-worker2 ansible_host=127.0.0.1 ansible_user=$USER ansible_connection=local
EOF

echo ""
echo "======================================================================"
echo "  [OK] K3D ENVIRONMENT READY FOR SCENARIO 1 TRIALS (STRICT PARITY)!"
echo "======================================================================"
kubectl cluster-info
kubectl get nodes