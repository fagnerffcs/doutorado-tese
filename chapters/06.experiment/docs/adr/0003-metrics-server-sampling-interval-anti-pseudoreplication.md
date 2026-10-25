# ADR-0003: Janela de Amostragem ($\ge 16\text{s}$) contra Pseudorreplicação do `metrics-server` nos Cenários 1 e 2

* **Status**: Aceito
* **Data**: 2026-10-25
* **Decisores**: Equipe de Pesquisa PANOPTES
* **Artefatos Técnicos**: [run-scenario1-baseline.py](file:///home/ffcandido/doutorado/panoptes/run-scenario1-baseline.py), [run-scenario2-overhead.py](file:///home/ffcandido/doutorado/panoptes/run-scenario2-overhead.py)

## Contexto e Declaração do Problema

Os scripts originais dos Cenários 1 (Baseline de Recursos sem Observabilidade) e 2 (Overhead da Arquitetura PANOPTES) coletavam $N = 30$ amostras executando `kubectl top pods` a cada `SAMPLE_INTERVAL_SECONDS = 5` segundos (duração total de 150s).

Contudo, o `metrics-server` do Kubernetes possui uma resolução padrão de coleta (`--metric-resolution`) de **15 segundos** junto ao cAdvisor do Kubelet. Como consequência, nos arquivos CSV anteriores, cada valor de CPU e memória repetia-se de forma idêntica 3 vezes consecutivas (totalizando apenas 10 leituras reais independentes em 30 linhas). Em análises paramétricas ou não-paramétricas, tratar leituras repetidas do mesmo cache como amostras independentes caracteriza **pseudorreplicação temporal**, subestimando artificialmente o desvio-padrão e inflando os graus de liberdade.

Adicionalmente, em `run-scenario2-overhead.py`, falhas transitórias de retorno do comando `kubectl top` retornavam `0.0, 0.0` silenciosamente, o que poderia contaminar a série temporal com zeros espúrios.

## Drivers de Decisão

* Garantir independência estatística entre as $N = 30$ observações de cada cenário de overhead.
* Prevenir gravação de amostras corrompidas (`0.0`) em caso de oscilação momentânea da API do Kubernetes.

## Resultado da Decisão

1. Alterado `SAMPLE_INTERVAL_SECONDS` de `5` para **`16` segundos** em [run-scenario1-baseline.py](file:///home/ffcandido/doutorado/panoptes/run-scenario1-baseline.py) e [run-scenario2-overhead.py](file:///home/ffcandido/doutorado/panoptes/run-scenario2-overhead.py), superando o ciclo de 15s do `metrics-server`.
2. Adicionada verificação de atualização de cache (`while last_reading == current_reading and retries < 3: time.sleep(2)`), garantindo que leituras consecutivas reflitam janelas atualizadas do cAdvisor.
3. Unificado o tratamento de erros com `check=True, timeout=15` e validação de saída não-vazia em ambos os scripts, realizando retentativa sem avançar o contador `sample_id` caso ocorra erro transitório.

### Consequências

* **Positivas**: As 30 amostras coletadas em `scenario1_workload_baseline.csv` e `scenario2_overhead_panoptes.csv` são genuinamente independentes, validando o uso direto de intervalos de confiança, teste *t* de Welch ou teste de Mann-Whitney.
* **Negativas**: O tempo de execução dos Cenários 1 e 2 passa de ~2,5 minutos para ~8 minutos por bateria.
