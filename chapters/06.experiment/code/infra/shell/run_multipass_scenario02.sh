#!/usr/bin/env bash
# ==============================================================================
# Multipass Cluster Provisioning Script - Scenario 2 (PANOPTES Architecture)
# ==============================================================================
echo "Deploying PANOPTES Master and Worker Nodes via Multipass..."

# 1. Launch Virtual Machines 
multipass launch --name k8s-master-panoptes --cpus 2 --memory 4G --disk 40G 22.04
multipass launch --name k8s-worker1-panoptes --cpus 2 --memory 4G --disk 30G 22.04
multipass launch --name k8s-worker2-panoptes --cpus 2 --memory 4G --disk 30G 22.04

# 2. Extract Master IP 
MASTER_IP=$(multipass info k8s-master-panoptes --format json | jq -r '.info["k8s-master-panoptes"].ipv4[0]')
echo "PANOPTES Master node provisioned at IP: $MASTER_IP"

# 3. Base Provisioning and K3s Server
multipass exec k8s-master-panoptes -- bash -c "
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y
sudo apt-get install -y software-properties-common curl jq git python3-pip linux-headers-\$(uname -r) bpfcc-tools

sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt-get install -y ansible
ansible-galaxy collection install kubernetes.core
sudo pip3 install kubernetes PyYAML jsonpatch

curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
bash get_helm.sh

curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC=\"--write-kubeconfig-mode 644 --node-ip=$MASTER_IP --disable traefik\" sh -
"

# 4. Extract cluster token
NODE_TOKEN=$(multipass exec k8s-master-panoptes -- sudo cat /var/lib/rancher/k3s/server/node-token)

# 5. Join Worker Nodes
for i in 1 2; do
  NODE="k8s-worker${i}-panoptes"
  echo "Installing K3s Agent and eBPF dependencies on $NODE..."
  WORKER_IP=$(multipass info $NODE --format json | jq -r ".info[\"$NODE\"].ipv4[0]")
  multipass exec $NODE -- bash -c "
  export DEBIAN_FRONTEND=noninteractive
  sudo apt-get update -y
  sudo apt-get install -y curl linux-headers-\$(uname -r) bpfcc-tools
  curl -sfL https://get.k3s.io | K3S_URL=https://$MASTER_IP:6443 K3S_TOKEN=$NODE_TOKEN INSTALL_K3S_EXEC=\"--node-ip=$WORKER_IP\" sh -
  "
done

# 6. WSL2 Routing and Kubeconfig Automation
echo "Configurando rede e credenciais (WSL2 -> Windows -> Multipass)..."
mkdir -p ~/.kube
multipass exec k8s-master-panoptes -- sudo cat /etc/rancher/k3s/k3s.yaml > ~/.kube/config

WIN_IP=$(ip route show default | awk '{print $3}')
sed -i "s/127.0.0.1/$WIN_IP/g" ~/.kube/config
sed -i 's/certificate-authority-data:.*/insecure-skip-tls-verify: true/g' ~/.kube/config

powershell.exe -Command "Start-Process netsh -ArgumentList 'interface portproxy add v4tov4 listenport=6443 listenaddress=0.0.0.0 connectport=6443 connectaddress=$MASTER_IP' -Verb RunAs"

echo "PANOPTES Kubernetes cluster provisionado e roteamento estabelecido!"
