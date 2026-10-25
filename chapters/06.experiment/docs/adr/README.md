# Architecture Decision Records (MADR) — Experimento PANOPTES

Este diretório documenta, no formato **MADR 3.0 (Markdown Any Decision Records)**, todas as decisões arquiteturais, metodológicas e de controle experimental adotadas na validação empírica da arquitetura **PANOPTES** (Cenários 1, 2, 3, 4a e 4b).

## Índice de Decisões

| ID | Título | Status | Cenários Impactados |
| :--- | :--- | :--- | :--- |
| [ADR-0001](file:///home/ffcandido/doutorado/panoptes/docs/adr/0001-paired-stratified-experimental-design.md) | Pareamento Estatístico Determinístico (`RANDOM_SEED=42`) e Simetria Temporal | Aceito | Cenários 3, 4a e 4b |
| [ADR-0002](file:///home/ffcandido/doutorado/panoptes/docs/adr/0002-elimination-of-data-leakage-pure-observability-rca.md) | Eliminação de *Data Leakage* via Kubernetes API e Pureza Multimodal no RCA | Aceito | Cenários 4a e 4b |
| [ADR-0003](file:///home/ffcandido/doutorado/panoptes/docs/adr/0003-metrics-server-sampling-interval-anti-pseudoreplication.md) | Janela de Amostragem ($\ge 16\text{s}$) contra Pseudorreplicação do `metrics-server` | Aceito | Cenários 1 e 2 |
| [ADR-0004](file:///home/ffcandido/doutorado/panoptes/docs/adr/0004-chaos-mesh-netem-direction-and-target-isolation.md) | Padronização de `direction: to` no Chaos Mesh e Isolamento de Labels sem `valkey-cart` | Aceito | Cenários 3, 4a e 4b |
| [ADR-0005](file:///home/ffcandido/doutorado/panoptes/docs/adr/0005-kernel-inotify-and-non-essential-workload-pruning.md) | Dimensionamento de `fs.inotify` e Poda de Subsistemas Não-Transacionais sob Teto de 4 GiB/Nó | Aceito | Todos os Cenários (1 a 4b) |
| [ADR-0006](file:///home/ffcandido/doutorado/panoptes/docs/adr/0006-virtualization-substrate-evolution-vagrant-multipass-k3d.md) | Evolução do Substrato de Virtualização (Vagrant/VirtualBox -> Multipass/Hyper-V -> K3d/WSL2 com Isolamento cgroup) | Aceito | Todos os Cenários (1 a 4b) |
