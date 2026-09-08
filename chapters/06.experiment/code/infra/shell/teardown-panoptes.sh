#!/usr/bin/env bash
set -euo pipefail

# Ensure execution starts from the script's root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Set Kubeconfig portably using active user's home directory
export KUBECONFIG="${KUBECONFIG:-${HOME}/.kube/config}"

# Standard callback to prevent Ansible plugin incompatibilities
export ANSIBLE_STDOUT_CALLBACK=default

# Validation check: verify kubeconfig existence
if [[ ! -f "${KUBECONFIG}" ]]; then
  echo "[ERROR] Kubeconfig file not found at: ${KUBECONFIG}" >&2
  echo "[HINT] Run: k3d kubeconfig get panoptes > ${HOME}/.kube/config" >&2
  exit 1
fi

echo "=== [$(date +'%Y-%m-%d %H:%M:%S')] Starting declarative PANOPTES teardown ==="
ansible-playbook teardown-panoptes.yml "$@"
echo "=== [$(date +'%Y-%m-%d %H:%M:%S')] Teardown successfully completed ==="