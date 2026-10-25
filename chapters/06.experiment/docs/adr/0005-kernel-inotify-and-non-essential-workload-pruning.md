# ADR-0005: Dimensionamento de `fs.inotify` no Kernel Host e Poda de Subsistemas Não-Transacionais do OTel Demo v3.1.0

* **Status**: Aceito
* **Data**: 2026-10-25
* **Decisores**: Equipe de Pesquisa PANOPTES
* **Artefatos Técnicos**: [check-panoptes-health.sh](file:///home/ffcandido/doutorado/panoptes/check-panoptes-health.sh), [run_k3d_scenario01.sh](file:///home/ffcandido/doutorado/panoptes/run_k3d_scenario01.sh), [run_k3d_scenario02.sh](file:///home/ffcandido/doutorado/panoptes/run_k3d_scenario02.sh)

## Contexto e Declaração do Problema

O ambiente experimental executa um cluster Kubernetes multi-nó via K3d sobre WSL2 com restrição estrita de hardware por nó (`--cpus="2.0" --memory="4g" --memory-swap="4g"` em cada container de nó `server-0`, `agent-0` e `agent-1`), conforme especificado no desenho da tese. Dois gargalos sistêmicos foram diagnosticados em produção:

1. **Exaustão de `fs.inotify.max_user_instances` (Padrão = 128)**:
   - Como todos os containers K3d e pods (Promtail, Grafana Beyla, OpenTelemetry Collector, Cert-Manager e Chaos Mesh Controller) compartilham o limite de instâncias `inotify` do usuário no kernel host Linux/WSL2, o valor padrão `128` esgotava-se rapidamente.
   - Isso causava `CrashLoopBackOff` contínuo no `chaos-controller-manager` com o erro `unable to start manager: {"error": "too many open files"}`, derrubando o webhook de admissão do Chaos Mesh (`502 Bad Gateway`).
2. **Saturação de Memória RAM (`3988Mi / 4096Mi`) e *Page Thrashing* no nó `agent-0`**:
   - O chart `open-telemetry/opentelemetry-demo` (v3.1.0) inclui por padrão diversos subsistemas secundários que não existiam nas versões anteriores ou não fazem parte do caminho crítico síncrono de e-commerce avaliado no experimento:
     - `opensearch-0` (~887 MiB RAM — backend interno redundante com o Grafana Loki/Tempo);
     - `agent` (~303 MiB RAM), `chatbot` (~137 MiB RAM) e `mcp` (~129 MiB RAM) — extensões de demonstração de LLM;
     - `fraud-detection` (~286 MiB RAM, JVM) e `accounting` (~106 MiB RAM) — consumidores assíncronos pós-venda;
     - `telemetry-docs` (~7 MiB) e `opamp-server` (~6 MiB).
   - Somados (~1,86 GiB de RAM), esses 8 pods faziam o nó `agent-0` operar a `3988Mi / 4096Mi` (97,4% da RAM sem swap), levando o kernel a consumir `1996m / 2000m` (99,8% de CPU) em reclamação direta de páginas (*thrashing*) e impedindo até mesmo a inicialização do proxy de entrada `frontend-proxy` (Envoy).

## Drivers de Decisão

* Preservar rigorosamente a especificação de hardware da tese (**2 vCPUs e 4 GiB de RAM por nó**).
* Preservar **100% do grafo transacional síncrono da loja Astronomy Shop** (`load-generator` $\to$ `frontend-proxy` $\to$ `frontend` $\to$ `checkout`, `cart`, `valkey-cart`, `payment`, `shipping`, `quote`, `currency`, `product-catalog`, `astronomy-db`, `recommendation`, `ad`, `email`, `image-provider`, `flagd` e `kafka`).
* Eliminar o *page thrashing* e a falha de inicialização de `inotify` em todos os cenários (1, 2, 3, 4a e 4b).

## Resultado da Decisão

1. **Elevação dos limites de `inotify` do Kernel**:
   - Padronizado `fs.inotify.max_user_instances = 8192` e `fs.inotify.max_user_watches = 524288`, validado automaticamente no passo `0` do script [check-panoptes-health.sh](file:///home/ffcandido/doutorado/panoptes/check-panoptes-health.sh#L38-L47).
2. **Poda Simétrica dos 8 Pods Não-Transacionais (`replicas=0`)**:
   - Os recursos `statefulset/opensearch` e `deployment/{agent,chatbot,mcp,fraud-detection,accounting,telemetry-docs,opamp-server}` são escalados para `0` réplicas no namespace `otel-demo`.
   - O broker `kafka` é **mantido ativo (`replicas=1`)** porque o serviço `checkout` possui dependência direta (`wait-for-kafka` e publicação de eventos de pedido).
   - Essa poda é aplicada de forma automatizada pelo [check-panoptes-health.sh](file:///home/ffcandido/doutorado/panoptes/check-panoptes-health.sh#L52-L57) e deve ser mantida idêntica tanto no cluster PANOPTES (Cenários 2, 4a, 4b) quanto no cluster Vanilla (Cenários 1 e 3).

### Consequências

* **Positivas**: Liberação imediata de ~1,86 GiB de RAM no cluster, eliminando o *thrashing* de memória e restabelecendo a geração contínua de tráfego HTTP/gRPC e traces distribuídos sem violar o limite de 4 GiB/nó.
* **Negativas**: Exige que o mesmo `kubectl scale --replicas=0` desses 8 componentes seja executado antes da coleta do Cenário 1 (`run-scenario1-baseline.py`) e do Cenário 3 (`run-scenario3-stratified-trials.py`) no cluster Vanilla para manter paridade absoluta de carga de trabalho.
