#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export KUBECONFIG="${KUBECONFIG:-${HOME}/.kube/config}"
export ANSIBLE_STDOUT_CALLBACK=default

if [[ ! -f "${KUBECONFIG}" ]]; then
  echo "[ERROR] Kubeconfig file not found at: ${KUBECONFIG}" >&2
  echo "[HINT] Run: k3d kubeconfig get panoptes > ${HOME}/.kube/config" >&2
  exit 1
fi

echo "=== [$(date +'%Y-%m-%d %H:%M:%S')] Provisioning Scenario 1 (Vanilla Baseline) ==="
ansible-playbook deploy-vanilla.yml "$@"
echo "=== [$(date +'%Y-%m-%d %H:%M:%S')] Scenario 1 configured and stabilized ==="