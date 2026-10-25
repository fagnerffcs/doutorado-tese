# ADR-0006: Evolução do Substrato de Virtualização (Vagrant/VirtualBox -> Multipass/Hyper-V -> K3d/WSL2 com Isolamento cgroup)

* **Status:** Aceito
* **Data:** 2026-10-25
* **Decisores:** Equipe de Pesquisa PANOPTES
* **Escopo:** Infraestrutura do Testbed (`run_k3d_scenario01.sh`, `run_k3d_scenario02.sh`, `run_multipass_scenario01.sh`, `run_multipass_scenario02.sh` e `code/infra/vagrant/`)

## Contexto e Declaração do Problema

Para avaliar rigorosamente a sobrecarga de recursos ($H_{1,3}$) e a eficácia diagnóstica ($H_{1,1}, H_{1,2}$) da arquitetura PANOPTES em uma topologia distribuída mínima de 3 nós (1 Control Plane e 2 Worker Nodes, cada um restrito a `2 vCPUs` e `4096 MiB` de RAM), o substrato de virtualização local passou por três ciclos iterativos de engenharia durante o *Design Cycle* da Design Science Research (DSR):

1. **Iteração 1 — Vagrant com Oracle VirtualBox (Type-2 Hypervisor):**
   - Em um host Windows 11 com recursos de virtualização nativa ativos (Hyper-V / WSL2 / Virtualization-Based Security), o VirtualBox opera em modo de emulação de execução nativa (*NEM turtle mode*).
   - Isso provocou severa degradação de I/O de disco virtual, alta latência de *fsync* no `etcd` do Kubernetes e perda recorrente de pacotes na rede overlay Flannel VXLAN entre as VMs, inviabilizando a estabilidade do cluster sob carga do *Astronomy Shop*.
2. **Iteração 2 — Canonical Multipass com Hyper-V (Type-1 Hypervisor):**
   - A migração do Vagrant para o Multipass sobre o Hyper-V nativo eliminou o gargalo de I/O de disco do VirtualBox.
   - Entretanto, como a suíte de orquestração científica (Ansible, Helm, `kubectl` e os motores algorítmicos RCA em Python) executava dentro do ambiente Linux WSL2 enquanto as VMs do Multipass residiam no switch virtual do Hyper-V no host Windows, todo o tráfego de controle e telemetria precisava atravessar uma ponte de duplo NAT via `netsh interface portproxy v4tov4` (WSL2 $\rightarrow$ Windows Host $\rightarrow$ Hyper-V vSwitch).
   - Durante campanhas prolongadas ($N=30$ trials) com injeção de falhas via Chaos Mesh (`tc-netem` e `pod-kill`), o proxy TCP do Windows (`iphlpsvc`) apresentava quedas intermitentes nos túneis `kubectl port-forward` para o Tempo/Loki/Prometheus e variações de memória por *dynamic memory ballooning* do Hyper-V, introduzindo ruído exógeno nas medições de $MTTDiag$.

## Opções Consideradas

* **Opção 1:** Manter o provisionamento via Vagrant + VirtualBox e aumentar os timeouts do `etcd`.
* **Opção 2:** Manter o Multipass + Hyper-V com redirecionamento `netsh portproxy` entre WSL2 e Windows.
* **Opção 3:** Migrar para **K3d (Rancher K3s containerizado sobre Docker nativo no kernel Linux WSL2)** aplicando cotas estritas de hardware por nó via Linux Control Groups (`docker update --cpus="2.0" --memory="4g" --memory-swap="4g"`) e isolamento do plano de controle via `NoSchedule` taint.

## Decisão

Escolhemos a **Opção 3 (K3d sobre WSL2 com restrição estrita de cgroups por nó)** como substrato definitivo de execução, preservando os scripts de Vagrant e Multipass no repositório como registro histórico da evolução do *Design Cycle*.

### Justificativa Metodológica

1. **Paridade Estrita de Hardware (2 vCPUs e 4 GiB RAM por Nó):** O comando `docker update --cpus="2.0" --memory="4g" --memory-swap="4g"` impõe limites rígidos no scheduler CFS (`cpu.max`) e no controlador de memória (`memory.max` / `memory.swap.max`) do kernel Linux para cada container de nó (`server-0`, `agent-0`, `agent-1`), mantendo exatamente a mesma especificação arquitetural planejada para as VMs do Multipass.
2. **Eliminação de Ruído de Rede Cross-Hypervisor:** Como os motores de diagnóstico em Python e os nós K3d compartilham a mesma pilha de rede Linux nativa dentro do WSL2, elimina-se completamente a ponte `netsh portproxy` do Windows, garantindo que a latência medida em $MTTDiag$ reflita exclusivamente o pipeline de observabilidade e a topologia Kubernetes.
3. **Compatibilidade com Kernel Inotify e Netem:** A execução nativa sobre o kernel Linux do WSL2 permite que o módulo `sch_netem` (usado pelo Chaos Mesh para `NetworkChaos`) e o tuning de `fs.inotify` (**ADR-0005**) operem diretamente sem camadas intermediárias de tradução de hypervisor.

## Consequências

* **Positivas:** Estabilidade determinística ao longo das baterias de 30 trials consecutivos; eliminação de quedas espúrias de `port-forward` causadas pelo NAT entre WSL2 e Hyper-V; reprodutibilidade imediata em qualquer estação Linux ou WSL2 via `run_k3d_scenario01.sh` e `run_k3d_scenario02.sh`.
* **Negativas / Trade-offs:** Como os nós K3d compartilham o mesmo kernel Linux do host WSL2, limites globais do kernel (como `fs.inotify.max_user_instances`) são compartilhados entre todos os nós, exigindo o ajuste explícito documentado no **ADR-0005**.
