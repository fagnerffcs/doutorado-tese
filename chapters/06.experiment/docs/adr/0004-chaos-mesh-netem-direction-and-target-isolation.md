# ADR-0004: Padronização de `direction: to` no Chaos Mesh e Isolamento Estrito de Pods Alvo

* **Status**: Aceito
* **Data**: 2026-10-25
* **Decisores**: Equipe de Pesquisa PANOPTES
* **Artefatos Técnicos**: [run-scenario3-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario3-trials.py), [run-scenario3-stratified-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario3-stratified-trials.py), [run-scenario4-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario4-trials.py), [run-scenario4-optimized-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario4-optimized-trials.py)

## Contexto e Declaração do Problema

Dois problemas técnicos afetavam a injeção de falhas via Chaos Mesh v2.6.3 no namespace `otel-demo`:
1. **Rejeição de `direction: both` pelo Validating Webhook (`vnetworkchaos.kb.io`)**:
   - Na especificação do CRD `NetworkChaos` (ação `delay` baseada em `tc netem`), o webhook de validação `vnetworkchaos.kb.io` proíbe `direction: both` ou `direction: from` quando o bloco `target:` não é especificado (`Spec.direction: Invalid value: "both": from and both direction cannot be used when targets is empty in netem action`).
   - Quando o manifesto utilizava `direction: both` sem `target:`, 100% dos trials de `network-delay` eram negados pela API e censurados artificialmente.
2. **Contaminação de Seletor por Substring no Alvo `cart` (`valkey-cart`)**:
   - Na resolução dinâmica de pods por substring (`if target_service in blob`), o alvo `"cart"` casava tanto com o microsserviço `cart` quanto com o banco de dados em memória `valkey-cart`, injetando falhas simultaneamente em dois componentes distintos ou atribuindo métricas do Redis/Valkey ao serviço `cart`.

## Drivers de Decisão

* Garantir que 100% dos manifestos `NetworkChaos`, `PodChaos` e `StressChaos` sejam aceitos pelo webhook validador do Chaos Mesh e efetivamente injetados no container alvo.
* Garantir que cada trial injete a falha em **exatamente um** microsserviço do `TARGET_POOL` (`payment`, `cart`, `shipping`, `currency`), sem atingir bancos de dados auxiliares (`valkey-cart`).

## Resultado da Decisão

1. **Padronização de `direction: to` em `NetworkChaos`**:
   - Todos os 4 scripts de injeção de falhas foram padronizados com `direction: to`, `latency: "2000ms"`, `jitter: "100ms"` e `duration: "180s"`, configuração validada via `kubectl apply --dry-run=server` junto ao webhook `vnetworkchaos.kb.io`.
2. **Isolamento Estrito de Labels e Prefixo de Pod (`is_exact_target_pod`)**:
   - A seleção de pods verifica igualdade exata nas labels `app.kubernetes.io/name == target_service` ou `app.kubernetes.io/component == target_service` (ou prefixo exato `{target_service}-`), excluindo explicitamente `valkey`, `redis`, `load-generator`, `frontend` e `checkout`.
3. **Remoção de Finalizers Presos, `kubectl create` e Repetição de Trials com Falha Pré-$T_0$ (`inject_chaos_manifest`)**:
   - No Chaos Mesh, o campo `spec` de um CRD já existente é imutável (`Cannot update chaos spec`). Caso um objeto do trial anterior permaneça em estado `Terminating` (por lentidão na remoção do finalizer `chaos-mesh/records`), o uso de `kubectl apply` com o mesmo `metadata.name` tenta aplicar um `PATCH` no `spec.selector.pods` e é bloqueado pelo webhook `vnetworkchaos.kb.io`.
   - `clean_cluster()` agora remove explicitamente finalizers presos caso o `kubectl delete` inicial expire, e `inject_chaos_manifest()` utiliza `kubectl create -f` precedido por `clean_cluster()` em caso de falha.
   - **Regra Metodológica de Censura**: Na Análise de Sobrevivência (Kaplan-Meier), a censura à direita (`censored = True, mttdiag = 300.0s`) deve representar **exclusivamente** a incapacidade do agente de diagnosticar uma falha que *foi efetivamente injetada* dentro da janela operacional. Quando uma falha de infraestrutura impede a própria injeção do caos antes de $T_0$, a tentativa inválida é **descartada e o mesmo `trial_id` é reexecutado** (`while trial <= NUM_TRIALS`), preservando os 30 tratamentos válidos.

### Consequências

* **Positivas**: Elimina falhas silenciosas de injeção e garante precisão cirúrgica no componente afetado durante cada trial.
* **Negativas**: Nenhuma.
