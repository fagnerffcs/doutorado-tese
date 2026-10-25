#!/usr/bin/env bash
# ==============================================================================
# Multipass Cluster Provisioning Script - Scenario 1 (Vanilla Kubernetes)
# ==============================================================================

# 1. Install local dependencies (WSL2 / Control Node)
echo "Installing Ansible and dependencies on the Control Node (WSL2)..."
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y
sudo apt-get install -y software-properties-common python3-pip jq git
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt-get install -y ansible
sudo pip3 install kubernetes PyYAML jsonpatch scipy pandas matplotlib
ansible-galaxy collection install kubernetes.core

# 2. Launch Virtual Machines 
echo "Deploying 1 Control Plane (Master) and 2 Worker Nodes via Multipass..."
multipass launch --name k8s-master --cpus 2 --memory 4G --disk 40G 22.04
multipass launch --name k8s-worker1 --cpus 2 --memory 4G --disk 30G 22.04
multipass launch --name k8s-worker2 --cpus 2 --memory 4G --disk 30G 22.04

# 3. Extract Master IP 
MASTER_IP=$(multipass info k8s-master --format json | jq -r '.info["k8s-master"].ipv4[0]')
echo "Master node provisioned at IP: $MASTER_IP"

# 4. Provision K3s Server
multipass exec k8s-master -- bash -c "
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC=\"--write-kubeconfig-mode 644 --node-ip=$MASTER_IP\" sh -
"

# 5. Extract cluster token
NODE_TOKEN=$(multipass exec k8s-master -- sudo cat /var/lib/rancher/k3s/server/node-token)

# 6. Provision K3s Agents
for NODE in k8s-worker1 k8s-worker2; do
  echo "Installing K3s Agent on $NODE..."
  WORKER_IP=$(multipass info $NODE --format json | jq -r ".info[\"$NODE\"].ipv4[0]")
  multipass exec $NODE -- bash -c "
  curl -sfL https://get.k3s.io | K3S_URL=https://$MASTER_IP:6443 K3S_TOKEN=$NODE_TOKEN INSTALL_K3S_EXEC=\"--node-ip=$WORKER_IP\" sh -
  "
done

# 7. WSL2 Routing and Kubeconfig Automation
echo "Configuring network and credentials (WSL2 -> Windows -> Multipass)..."
mkdir -p ~/.kube
multipass exec k8s-master -- sudo cat /etc/rancher/k3s/k3s.yaml > ~/.kube/config

WIN_IP=$(ip route show default | awk '{print $3}')
sed -i "s/127.0.0.1/$WIN_IP/g" ~/.kube/config
sed -i 's/certificate-authority-data:.*/insecure-skip-tls-verify: true/g' ~/.kube/config

powershell.exe -Command "Start-Process netsh -ArgumentList 'interface portproxy add v4tov4 listenport=6443 listenaddress=0.0.0.0 connectport=6443 connectaddress=$MASTER_IP' -Verb RunAs"

# 8. Dynamic Inventory Generation
echo "Generating dynamic Ansible inventory..."
cat <<EOF > inventory.ini
[k8s_cluster]
k8s-master ansible_host=$MASTER_IP ansible_user=ubuntu
k8s-worker1 ansible_host=$(multipass info k8s-worker1 --format json | jq -r '.info["k8s-worker1"].ipv4[0]') ansible_user=ubuntu
k8s-worker2 ansible_host=$(multipass info k8s-worker2 --format json | jq -r '.info["k8s-worker2"].ipv4[0]') ansible_user=ubuntu
EOF

echo "Vanilla Kubernetes cluster provisioning and Control Node setup complete!"
