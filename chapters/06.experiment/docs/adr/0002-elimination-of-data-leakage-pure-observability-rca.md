# ADR-0002: Eliminação de *Data Leakage* via Kubernetes API e Pureza Multimodal no RCA

* **Status**: Aceito
* **Data**: 2026-10-25
* **Decisores**: Equipe de Pesquisa PANOPTES
* **Artefatos Técnicos**: [run-scenario4-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario4-trials.py), [run-scenario4-optimized-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario4-optimized-trials.py)

## Contexto e Declaração do Problema

Na revisão de código dos scripts do Cenário 4, foram identificados desvios que comprometiam a **Validade de Construto** (*Construct Validity*):
1. **No Cenário 4b (`run-scenario4-optimized-trials.py`)**:
   - A função `check_pod_disruption_events` executava `kubectl get pods -n otel-demo -o json` durante o loop de diagnóstico para inspecionar metadados da API do Kubernetes (`deletionTimestamp`, `creationTimestamp` e mudança de `uid`) e rotulava essa detecção no CSV como `LOKI_LOG_SIGNATURE`, mesmo quando nenhum log havia sido retornado pelo Grafana Loki.
   - A função `query_prometheus_cpu_rates` executava `kubectl top pods` como *fallback* paralelo ao Prometheus, registrando a detecção como `PROMETHEUS_METRIC_SATURATION` mesmo quando a leitura provinha do `metrics-server` do Kubernetes.
2. **No Cenário 4a (`run-scenario4-trials.py`)**:
   - A função `analyze_standard_trace` retornava a string `"unknown-service"` quando um trace não apresentava erro nem span acima do limiar; como `bool("unknown-service") == True` em Python, o loop encerrava prematuramente no primeiro trace inconclusivo.
   - As buscas no Tempo (`/api/search`) não filtravam o intervalo `[t0, now]`, permitindo diagnosticar traces anteriores à injeção da falha.

## Drivers de Decisão

* Garantir que o Cenário 4b avalie **exclusivamente** a capacidade diagnóstica dos três pilares de observabilidade CNCF (Prometheus via PromQL, Loki via LogQL e Tempo via TraceQL/OTLP HTTP API), sem consultar o plano de controle do Kubernetes (`kubectl`) durante o loop de RCA.
* Garantir que o Cenário 4a implemente fielmente a heurística clássica de *Distributed Tracing* sem bugs de programação que abortem o polling prematuramente.

## Resultado da Decisão

1. **Pureza Multimodal no Cenário 4b ([run-scenario4-optimized-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario4-optimized-trials.py))**:
   - Removidas todas as chamadas a `kubectl` (`kubectl get pods` e `kubectl top pods`) de dentro do agente de RCA (`run_panoptes_rca_agent`).
   - A saturação de CPU é medida exclusivamente via PromQL no endpoint HTTP do Prometheus (`max by (pod) (irate(container_cpu_usage_seconds_total[1m]))` e `rate(...[45s])`).
   - Eventos de reinício/recriação de containers são consultados via PromQL (`kube_pod_container_status_restarts_total`, `kube_pod_start_time` e `container_start_time_seconds`) e correlacionados com logs reais extraídos via LogQL no Loki.
   - Adicionados delimitadores de palavra (`\beof\b`, `\boom\b`) em `CRITICAL_LOG_PATTERNS` para evitar falsos positivos em substrings.
2. **Correção do Agente Standard Tracing no Cenário 4a ([run-scenario4-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario4-trials.py))**:
   - `analyze_standard_trace` retorna `None` quando o trace analisado é inconclusivo, mantendo o agente em polling até encontrar uma evidência válida ou atingir os 300s.
   - Todas as consultas ao Tempo filtram estritamente `start = int(t0)` e `span.startTimeUnixNano >= strict_t0_ns`.

### Consequências

* **Positivas**: As evidências auditadas em `scenario4b_evidence_audit.jsonl` refletem de forma íntegra e verificável apenas consultas HTTP às APIs do Prometheus, Loki e Tempo; a comparação entre 4a (monomodal via Tempo) e 4b (multimodal + decomposição de *exclusive self-time*) torna-se cientificamente irrefutável.
* **Negativas**: O tempo de convergência para `pod-kill` e `cpu-stress` no Cenário 4b passa a refletir o tempo real de ingestão do Promtail/Loki e o intervalo de *scrape* (15s) do Prometheus, em vez da leitura instantânea da API do Kubernetes.
