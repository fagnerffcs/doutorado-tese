# ADR-0001: Pareamento Estatístico Determinístico (`RANDOM_SEED=42`) e Simetria Temporal entre Cenários de RCA

* **Status**: Aceito
* **Data**: 2026-10-25
* **Decisores**: Equipe de Pesquisa PANOPTES
* **Artefatos Técnicos**: [run-scenario3-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario3-trials.py), [run-scenario3-stratified-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario3-stratified-trials.py), [run-scenario4-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario4-trials.py), [run-scenario4-optimized-trials.py](file:///home/ffcandido/doutorado/panoptes/run-scenario4-optimized-trials.py)

## Contexto e Declaração do Problema

Nos scripts originais dos experimentos de diagnóstico de causa-raiz (RCA — Cenários 3, 4a e 4b), existiam assimetrias metodológicas que introduziam variáveis de confusão (*confounding variables*) na comparação de latência diagnóstica ($\text{MTTDiag}$) e acurácia:
1. Os Cenários 3 e 4a utilizavam sorteio pseudoaleatório não-balanceado e sem semente fixa (`random.choice`), enquanto o Cenário 4b usava blocos balanceados sem semente fixa. Com $N=30$ trials, a proporção de falhas (`network-delay`, `pod-kill`, `cpu-stress`) e serviços-alvo (`payment`, `cart`, `shipping`, `currency`) variava entre os cenários.
2. O tempo de espera pós-injeção antes do início do polling era de `10s` nos Cenários 3 e 4a, mas de `3s` no Cenário 4b, impondo uma penalidade artificial de $+7\text{s}$ contra os baselines.
3. O intervalo de polling e o aguardo de recuperação de rollout (`wait_for_workload_recovery`) diferiam entre os scripts.

## Drivers de Decisão

* Garantir **Validade Interna** estrita para testes de sobrevivência (Kaplan-Meier / Log-Rank) e testes pareados (Wilcoxon / McNemar).
* Eliminar qualquer vantagem temporal artificial entre o agente proposto (PANOPTES 4b) e os agentes de linha de base (Vanilla 3 e Standard Tracing 4a).
* Garantir balanceamento fatorial exato ($3 \text{ tipos de caos} \times 10 \text{ repetições} = 30 \text{ trials}$).

## Opções Consideradas

* **Opção 1**: Manter amostragem aleatória independente sem semente e comparar apenas médias agregadas.
* **Opção 2**: Adotar um delineamento experimental em blocos completos balanceados com gerador pseudoaleatório isolado (`random.Random(42)`) e parâmetros temporais idênticos em todos os scripts.

## Resultado da Decisão

Escolhida a **Opção 2**. Todos os scripts de RCA (Cenários 3, 4a e 4b) foram padronizados com:
1. Função idêntica `build_balanced_trial_schedule(NUM_TRIALS=30, seed=42)` gerando exatamente a mesma sequência pareada `(target_service, chaos_type)` para `trial_id = 1..30`.
2. Parâmetros temporais unificados:
   - `INITIAL_PROPAGATION_SLEEP = 3` segundos pós-injeção;
   - `POLLING_INTERVAL_SECONDS = 4` segundos;
   - `TIMEOUT_SECONDS = 300` segundos (teto operacional de censura à direita);
   - Estabilização entre trials de `20s` precedida por `clean_cluster()` e `wait_for_workload_recovery()`.

### Consequências

* **Positivas**: Permite comparação pareada trial a trial ($i = 1 \dots 30$) sob exatamente a mesma perturbação e o mesmo serviço-alvo; elimina o viés de $+7\text{s}$ que prejudicava os Cenários 3 e 4a.
* **Negativas**: Exige a reexecução completa das baterias de 30 trials sempre que a semente ou o conjunto de alvos for modificado.
