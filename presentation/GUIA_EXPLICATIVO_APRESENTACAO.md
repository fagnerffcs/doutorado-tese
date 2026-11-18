# 🎓 Guia Explicativo da Apresentação de Qualificação de Doutorado
## Projeto PANOPTES: Arquitetura de Referência para Observabilidade em Kubernetes

> **Autor:** Fagner Fernandes Candido da Silva  
> **Orientador:** Prof. Dr. Vinícius Cardoso Garcia  
> **Coorientador:** Prof. Dr. Jackson Raniel Florêncio da Silva  
> **Instituição:** Centro de Informática (CIn) — Universidade Federal de Pernambuco (UFPE)  
> **Área:** Engenharia de Software e Linguagens de Programação (PPGCC)  
> **Objetivo deste documento:** Explicar detalhadamente, slide por slide, todo o conteúdo da apresentação de qualificação em linguagem acessível, dispensando conhecimentos matemáticos e técnicos avançados.

---

## 📑 Sumário

1. [O Trabalho em 3 Minutos: A Analogia Central](#1-o-trabalho-em-3-minutos-a-analogia-central)
2. [Pequeno Glossário Sem Complicações](#2-pequeno-glossário-sem-complicações)
3. [Explicação Detalhada Slide por Slide](#3-explicação-detalhada-slide-por-slide)
   - [Slide 01: Capa e Identificação](#slide-01-capa-e-identificação)
   - [Slide 02: Agenda da Apresentação](#slide-02-agenda-da-apresentação)
   - [Slide 03: O Paradigma Cloud-Native & a Complexidade do Kubernetes](#slide-03-o-paradigma-cloud-native--a-complexidade-do-kubernetes)
   - [Slide 04: Fundamentação Teórica: O Conceito Canônico de Kalman](#slide-04-fundamentação-teórica-o-conceito-canônico-de-kalman)
   - [Slide 05: Mapeamento da Observabilidade para Sistemas Cloud-Native](#slide-05-mapeamento-da-observabilidade-para-sistemas-cloud-native)
   - [Slide 06: O Diagnóstico Padrão do Kubernetes e suas Limitações](#slide-06-o-diagnóstico-padrão-do-kubernetes-e-suas-limitações)
   - [Slide 07: O Estado Atual do Ecossistema Open-Source (CNCF)](#slide-07-o-estado-atual-do-ecossistema-open-source-cncf)
   - [Slide 08: Lacunas Arquiteturais & A Missão do PANOPTES](#slide-08-lacunas-arquiteturais--a-missão-do-panoptes)
   - [Slide 09: Perguntas de Pesquisa (RQs)](#slide-09-perguntas-de-pesquisa-rqs)
   - [Slide 10: Objetivos da Pesquisa (Geral e Específicos)](#slide-10-objetivos-da-pesquisa-geral-e-específicos)
   - [Slide 11: Hipóteses Formais de Pesquisa](#slide-11-hipóteses-formais-de-pesquisa)
   - [Slide 12: Metodologia: Ciclo de Vida DSRM (Peffers et al., 2006)](#slide-12-metodologia-ciclo-de-vida-dsrm-peffers-et-al-2006)
   - [Slide 13: Metodologia: Os Três Ciclos de Pesquisa DSR (Hevner et al., 2004)](#slide-13-metodologia-os-três-ciclos-de-pesquisa-dsr-hevner-et-al-2004)
   - [Slide 14: Estado da Arte: Protocolo da Rapid Review Sistemática](#slide-14-estado-da-arte-protocolo-da-rapid-review-sistemática)
   - [Slide 15: Estado da Arte: Lacunas da Literatura & Contribuições](#slide-15-estado-da-arte-lacunas-da-literatura--contribuições)
   - [Slide 16: O Modelo de Maturidade de Observabilidade (OMM)](#slide-16-o-modelo-de-maturidade-de-observabilidade-omm)
   - [Slide 17: Visão Geral da Arquitetura PANOPTES](#slide-17-visão-geral-da-arquitetura-panoptes)
   - [Slide 18: Princípios de Controle (CPs) & Heurísticas de Contingência (ConHs)](#slide-18-princípios-de-controle-cps--heurísticas-de-contingência-conhs)
   - [Slide 19: Decisões Arquiteturais Registradas (MADR-0001 a MADR-0006)](#slide-19-decisões-arquiteturais-registradas-madr-0001-a-madr-0006)
   - [Slide 20: Design Fatorial $2 \times 2$ & Ambiente Experimental](#slide-20-design-fatorial-2-times-2--ambiente-experimental)
   - [Slide 21: Protocolo de Injeção de Falhas (Chaos Mesh)](#slide-21-protocolo-de-injeção-de-falhas-chaos-mesh)
   - [Slide 22: O Viés de Duração em Cascata: Por que o Tracing Isolado Falhou?](#slide-22-o-viés-de-duração-em-cascata-por-que-o-tracing-isolado-falhou)
   - [Slide 23: Hipótese $H_{1,3}$: Sobrecarga de CPU no Workload](#slide-23-hipótese-h_13-sobrecarga-de-cpu-no-workload)
   - [Slide 24: Hipótese $H_{1,3}$: Pegada de Memória RAM no Cluster](#slide-24-hipótese-h_13-pegada-de-memória-ram-no-cluster)
   - [Slide 25: Hipótese $H_{1,1}$: Redução Massiva de Latência (MTTDiag)](#slide-25-hipótese-h_11-redução-massiva-de-latência-mttdiag)
   - [Slide 26: Hipótese $H_{1,2}$: Superioridade em Acurácia Diagnóstica (Acc)](#slide-26-hipótese-h_12-superioridade-em-acurácia-diagnóstica-acc)
   - [Slide 27: Análise de Sobrevivência e Censura (Curvas de Kaplan-Meier)](#slide-27-análise-de-sobrevivência-e-censura-curvas-de-kaplan-meier)
   - [Slide 28: Ameaças à Validade & Estratégias de Mitigação](#slide-28-ameaças-à-validade--estratégias-de-mitigação)
   - [Slide 29: Síntese das Contribuições da Tese (1/2: Arquitetura & Artefato)](#slide-29-síntese-das-contribuições-da-tese-12-arquitetura--artefato)
   - [Slide 30: Síntese das Contribuições da Tese (2/2: Evidência & Maturidade)](#slide-30-síntese-das-contribuições-da-tese-22-evidência--maturidade)
   - [Slide 31: Produção Científica & Artigos Derivados da Tese](#slide-31-produção-científica--artigos-derivados-da-tese)
   - [Slide 32: Roadmap de Extensões até a Defesa Final](#slide-32-roadmap-de-extensões-até-a-defesa-final)
   - [Slide 33: Cronograma até a Defesa Final](#slide-33-cronograma-até-a-defesa-final)
   - [Slide 34: Agradecimentos e Encerramento](#slide-34-agradecimentos-e-encerramento)
4. [As Principais Descobertas Científicas ("O Ouro da Tese")](#4-as-principais-descobertas-científicas-o-ouro-da-tese)
5. [Possíveis Perguntas da Banca e Como Responder](#5-possíveis-perguntas-da-banca-e-como-responder)

---

## 1. O Trabalho em 3 Minutos: A Analogia Central

Imagine um hospital moderno com uma UTI de alta complexidade:
* **Antigamente (Sistemas Monolíticos):** Havia apenas um paciente em um quarto simples. Se ele passava mal, o médico olhava diretamente para ele, media a pressão e sabia exatamente o que estava acontecendo.
* **Hoje (Nuvem, Microsserviços e Kubernetes):** A UTI tem dezenas de pacientes interligados, onde o remédio dado a um altera os batimentos de outro através de tubos invisíveis. Além disso, os pacientes trocam de leito a cada 5 minutos de forma automática.
* **O Problema Atual (Monitoramento Tradicional):** O alarme do quarto apita dizendo *"pressão caiu!"*. Mas isso só avisa que o paciente piorou, não explica **qual** remédio causou a reação alérgica em cascata nem em qual leito a falha começou. Os médicos perdem horas correndo entre prontuários de papel separados (um bloco de notas para batimentos, outro para exames de sangue, outro para remédios).
* **A Solução desta Tese (O PANOPTES):** Criamos uma central de inteligência diagnóstica integrada. Ela junta os batimentos (métricas), os diários de bordo dos médicos (logs) e a rota exata de cada medicamento (traces) em uma única tela correlacionada. Quando ocorre uma pane em cascata, o sistema deduz em **17 segundos** quem foi o paciente zero da infecção, acertando em **83,3%** das vezes, sem sobrecarregar a energia do hospital.

---

## 2. Pequeno Glossário Sem Complicações

* **Nuvem / Cloud-Native:** Forma moderna de construir programas de computador divididos em pequenos pedaços independentes que rodam na internet.
* **Microsserviços:** Em vez de ter um programa gigante (um monólito), divide-se o sistema em dezenas de mini-programas (ex: um só calcula o frete, outro só processa o pagamento, outro exibe a foto do produto).
* **Kubernetes (K8s):** O "maestro" desse ecossistema. É um software inteligente que decide onde cada mini-programa vai rodar, reinicia os que travam e cria novos quando há muitos acessos.
* **Telemetria:** O conjunto de dados que o sistema gera sobre si mesmo enquanto funciona:
  * **Métricas ($M$):** Números ao longo do tempo (ex: velocímetro do carro, temperatura do motor).
  * **Logs ($L$):** Frases e registros de eventos (ex: "usuário clicou em comprar", "falha ao conectar no banco de dados").
  * **Traces ($T$):** O rastreador da viagem. Mostra o caminho exato que uma requisição percorreu por todos os microsserviços e quanto tempo passou em cada um.
  * **Eventos ($E$):** Avisos de mudanças estruturais (ex: "um novo servidor foi ligado").
* **Observabilidade:** A capacidade de entender **por que** algo deu errado dentro do sistema apenas olhando para os sinais que ele emite para fora (sem precisar parar tudo e abrir o código).
* **Chaos Engineering (Engenharia de Caos):** A prática de injetar falhas de propósito no sistema (desconectar um servidor, deixar a rede lenta) para testar se ele aguenta o tranco no mundo real.
* **MTTDiag (Mean Time to Diagnose):** Tempo Médio para Diagnosticar. Quanto tempo os engenheiros levam entre o alarme tocar e descobrir quem causou o problema.
* **Self-Time (Tempo Próprio):** O tempo que um microsserviço realmente gastou trabalhando, descontando o tempo que ele ficou de braços cruzados esperando outro responder.

---

## 3. Explicação Detalhada Slide por Slide

---

### Slide 01: Capa e Identificação
* **O que está na tela:** Título do projeto (*PANOPTES: An Open-Source Reference Architecture for Observability in Kubernetes Ecosystems*), nome do candidato, orientadores e brasão/identidade visual do CIn-UFPE.
* **A ideia simples:** Apresentação formal da qualificação de doutorado.
* **Por que o nome PANOPTES?** Na mitologia grega, *Panoptes* era o gigante de cem olhos que conseguia enxergar tudo em todas as direções ao mesmo tempo. É a metáfora perfeita para uma arquitetura que enxerga cada canto de um cluster Kubernetes.
* **Dica de fala:** *"Bom dia a todos os membros da banca. Hoje apresento o projeto de qualificação do PANOPTES, uma arquitetura de referência de código aberto para observabilidade em ecossistemas Kubernetes."*

---

### Slide 02: Agenda da Apresentação
* **O que está na tela:** Os 6 grandes blocos da apresentação: Contexto/Problema, Objetivos/Hipóteses, Metodologia/Estado da Arte, Arquitetura PANOPTES, Resultados Experimentais e Conclusões/Cronograma.
* **A ideia simples:** O mapa do tesouro da apresentação, organizando o pensamento em ordem lógica e científica.
* **Dica de fala:** *"Nossa apresentação está estruturada em seis seções lógicas, partindo das dores práticas da indústria e da fundamentação teórica até as evidências experimentais e o plano até a defesa final."*

---

### Slide 03: O Paradigma Cloud-Native & a Complexidade do Kubernetes
* **O que está na tela:** A transição de monólitos para microsserviços; a explosão de dados; o conceito de "falhas latentes" (*Unknown Unknowns*); e dados da CNCF mostrando que mais de 84% das empresas usam Kubernetes, mas têm como maior pesadelo o tempo gasto para resolver problemas operacionais.
* **A analogia:** Imagine trocar uma bicicleta por um avião supersônico com 500 peças elétricas. Ele é incrivelmente mais rápido, mas se uma luz piscar no painel, descobrir qual fio desencapou é um pesadelo.
* **Conceito-chave:**
  * *Known Unknowns (Problemas Conhecidos):* "O disco encheu". Isso é fácil, um alarme avisa.
  * *Unknown Unknowns (Problemas Desconhecidos/Latentes):* Uma lentidão assíncrona que não estoura o limite de memória, mas faz o cliente desistir da compra.
* **Dica de fala:** *"Migramos para microsserviços buscando agilidade, mas o Kubernetes trouxe uma complexidade operacional sem precedentes: os componentes nascem e morrem em segundos, gerando um oceano de telemetria onde falhas silenciosas passam despercebidas pelos alarmes comuns."*

---

### Slide 04: Fundamentação Teórica: O Conceito Canônico de Kalman
* **O que está na tela:** À esquerda, o Teorema de Kalman de 1959 (da Engenharia Aeroespacial e Teoria de Controle) e o desafio em sistemas distribuídos. À direita, um diagrama de Venn comparando *Monitoring* (Monitoramento tradicional) versus *Observability* (Observabilidade).
* **A explicação simples:**
  * Em 1959, Rudolf Kalman inventou a matemática que permitiu ao homem pousar na Lua: você não precisa entrar dentro da turbina do foguete para saber se ela vai explodir; você só precisa olhar para as saídas (sensores de calor, vibração) e saber as entradas (combustível).
  * **Monitoramento tradicional:** É o painel do carro que avisa *"temperatura alta"*. Ele só sabe avisar sobre coisas pré-programadas (*Known Unknowns*).
  * **Observabilidade:** É ter sensores avançados que permitem entender *por que* o motor esquentou, mesmo que a causa seja um óleo adulterado que nunca havia sido visto antes (*Unknown Unknowns*).
* **Dica de fala:** *"Nossa pesquisa não trata observabilidade como jargão de marketing. Resgatamos a definição canônica de Rudolf Kalman na Teoria de Controle: ser capaz de reconstruir com precisão matemática o estado interno do sistema olhando apenas para as suas manifestações externas."*

---

### Slide 05: Mapeamento da Observabilidade para Sistemas Cloud-Native
* **O que está na tela:** Como traduzimos a matemática de Kalman para a computação moderna:
  * Estado Interno $x(t)$: Saúde dos servidores, tráfego interno, filas de espera, conexões de banco.
  * Entradas $u(t)$: Usuários clicando, novas versões de software sendo instaladas.
  * Saídas/Telemetria $\mathcal{O}$: Métricas, Logs, Traces e Eventos.
  * **Dualidade Controlabilidade-Observabilidade:** Um sistema que você não enxerga é um sistema que você não consegue controlar.
* **A analogia:** Você não pode pedir para um piloto automático pousar um avião (Controlabilidade) se os instrumentos de altitude e velocidade estiverem quebrados ou mostrando dados conflitantes (Observabilidade).
* **Dica de fala:** *"Para que os recursos autônomos do Kubernetes — como auto-scaling e reinicialização de pods — funcionem de verdade, é um pré-requisito matemático que o estado interno do cluster seja totalmente observável."*

---

### Slide 06: O Diagnóstico Padrão do Kubernetes e suas Limitações
* **O que está na tela:** A tela preta de terminal que os engenheiros usam no dia a dia (`kubectl logs`, `kubectl top`) e por que ela é perigosa:
  1. Informações pontuais e soltas;
  2. Se o container quebrar, o log some junto com ele;
  3. Não mostra como um serviço afetou o outro;
  4. Demora horas de análise manual.
* **A analogia:** Tentar descobrir quem quebrou a janela da escola entrevistando um aluno por vez no recreio, enquanto as crianças correm de um lado para o outro.
* **Dica de fala:** *"O ferramental padrão do Kubernetes se baseia em comandos manuais de terminal. É como tentar apagar um incêndio em um arranha-céu usando uma lanterna e um balde d'água."*

---

### Slide 07: O Estado Atual do Ecossistema Open-Source (CNCF)
* **O que está na tela:** As melhores ferramentas gratuitas e abertas que existem hoje no mercado: Prometheus (números), Loki e Fluent Bit (textos/logs), Tempo e Jaeger (rastreadores/traces), OpenTelemetry (padronizador) e Grafana (telas).
* **A ideia simples:** Reconhecer que a comunidade já criou excelentes programas para cada tipo de dado. O problema não é a falta de ferramentas!
* **Dica de fala:** *"A Cloud Native Computing Foundation possui excelentes tecnologias consolidadas. Temos ótimos coletores de métricas, excelentes bancos de logs e padrões emergentes como o OpenTelemetry."*

---

### Slide 08: Lacunas Arquiteturais & A Missão do PANOPTES
* **O que está na tela:** O problema dos "silos": as ferramentas são ótimas, mas não conversam entre si. Cada uma fala um dialeto diferente.
* **A consequência prática:** O banco de dados fica lento $\rightarrow$ o carrinho de compras trava $\rightarrow$ o cliente não consegue pagar. O trace diz que o checkout falhou, o log do checkout não mostra erro nenhum e a métrica de CPU está normal. O operador fica perdido em um labirinto!
* **A Missão do PANOPTES:** Costurar esses três tipos de dados com um "fio invisível" (correlação semântica) para que o sistema aponte a causa real na hora.
* **Dica de fala:** *"O problema do mercado é a fragmentação. Cada ferramenta guarda dados em silos isolados. O PANOPTES nasceu para ser a ponte semântica que une essas ferramentas sem inventar a roda, guiando o engenheiro diretamente à causa-raiz."*

---

### Slide 09: Perguntas de Pesquisa (RQs)
* **O que está na tela:**
  * **MRQ (Pergunta Principal):** Como desenhar uma arquitetura aberta que reduza drasticamente o tempo de diagnóstico ($MTTDiag$) com precisão sem derrubar o cluster pelo consumo de memória e CPU?
  * **SRQ1:** Quais os componentes essenciais?
  * **SRQ2:** Como fazer a correlação inteligente entre métricas, logs e traces?
  * **SRQ3:** Como provar isso matematicamente e estatisticamente?
  * **SRQ4:** Como classificar o nível de maturidade das empresas?
* **A ideia simples:** Demonstrar o rigor acadêmico. Toda tese de doutorado deve responder perguntas científicas muito bem delimitadas.

---

### Slide 10: Objetivos da Pesquisa (Geral e Específicos)
* **O que está na tela:**
  * **Objetivo Geral:** Projetar, implementar e validar o PANOPTES.
  * **SO1 a SO4:** Os 4 degraus práticos para atingir o objetivo: requisitos, implementação com código automatizado, testes com injeção de falhas (Caos) e criação do Modelo de Maturidade (OMM).
* **Dica de fala:** *"Nosso objetivo não é puramente teórico; ele se desdobra em quatro metas pragmáticas, desde a especificação formal até a automação completa por código e validação empírica."*

---

### Slide 11: Hipóteses Formais de Pesquisa
* **O que está na tela:** As três apostas científicas que a tese promete validar:
  * $H_{1,1}$: O PANOPTES vai reduzir expressivamente o tempo gasto para achar a causa-raiz ($MTTDiag$).
  * $H_{1,2}$: A precisão diagnóstica ($Acc$) será superior a qualquer ferramenta isolada.
  * $H_{1,3}$: A sobrecarga de CPU ($\Delta_{\text{CPU}} \le 15\%$ do workload) e de RAM ($\Delta_{\text{RAM}} \le 30\%$ do cluster) da própria observabilidade será estritamente contida.
* **A analogia:** O remédio precisa curar a doença ($H_{1,1}$ e $H_{1,2}$), mas não pode matar o paciente com efeitos colaterais ($H_{1,3}$).

---

### Slide 12: Metodologia: Ciclo de Vida DSRM (Peffers et al., 2006)
* **O que está na tela:** O método científico adotado: *Design Science Research Methodology (DSRM)* em 6 passos clássicos:
  1. Identificar o Problema (fragmentação em K8s);
  2. Definir os Objetivos da Solução;
  3. Criar o Artefato (a arquitetura PANOPTES e o correlacionador);
  4. Demonstrar em um cluster emulador de testes (K3d);
  5. Avaliar com experimentos estatísticos e injeção de falhas;
  6. Comunicar (publicações científicas, registros de decisões e código aberto).
* **A ideia simples:** Mostrar para a banca que a construção do sistema seguiu a metodologia padrão-ouro da ciência da computação para criação de artefatos.

---

### Slide 13: Metodologia: Os Três Ciclos de Pesquisa DSR (Hevner et al., 2004)
* **O que está na tela:** O diagrama clássico de Hevner com os 3 anéis que garantem qualidade científica:
  * **Ciclo de Relevância:** Ouvir as dores reais do mercado e das empresas.
  * **Ciclo de Rigor:** Apoiar-se em teorias matemáticas consolidadas (Kalman) e literatura científica.
  * **Ciclo de Design:** O laboratório onde o sistema é construído, testado e ajustado iterativamente.
* **Dica de fala:** *"Segundo Hevner, uma tese aplicada só tem valor se equilibrar o rigor teórico dos fundamentos com a relevância prática para o ecossistema industrial."*

---

### Slide 14: Estado da Arte: Protocolo da Rapid Review Sistemática
* **O que está na tela:** Como foi feita a varredura da literatura científica mundial:
  * Protocolo ágil e auditável com apoio da plataforma *Parsifal*;
  * 4 bases científicas de peso (IEEE, ACM, Springer, ScienceDirect);
  * 312 artigos encontrados inicialmente $\rightarrow$ funil rigoroso com critérios de exclusão $\rightarrow$ 10 estudos primários selecionados a dedo para análise profunda.
* **A ideia simples:** Provar que conhecemos tudo o que já foi publicado no mundo sobre observabilidade em Kubernetes entre 2018 e 2025.

---

### Slide 15: Estado da Arte: Lacunas da Literatura & Contribuições
* **O que está na tela:** O que a revisão da literatura revelou:
  * **A grande falha dos outros artigos:** Quase todos os artigos acadêmicos eram puramente conceituais ("ideias no papel"), sem testes reais de estresse e sem métricas de tempo de diagnóstico.
  * **A resposta desta tese:**
    1. Criamos um modelo formal de maturidade (OMM);
    2. Construímos o sistema de verdade (PANOPTES);
    3. Testamos com injeção de panes pesadas no cluster.
* **Dica de fala:** *"Identificamos uma clara lacuna de validação na academia: muitos trabalhos desenhavam arquiteturas no papel, mas quase nenhum realizava experimentos reprodutíveis com injeção controlada de anomalias."*

---

### Slide 16: O Modelo de Maturidade de Observabilidade (OMM)
* **O que está na tela:** Uma matriz evolutiva $5 \times 5$ (baseada em Becker et al., 2009 e De Bruin et al., 2005) que permite diagnosticar e evoluir qualquer cluster Kubernetes:
  * **Nível 1 (Opaque / Opaco):** Ninguém mede nada ($\mathcal{O}(t) = \emptyset$). O cliente é quem avisa que o sistema caiu.
  * **Nível 2 (Reactive / Reativo):** Inspeção ad-hoc via CLI (`kubectl logs/top`) e `cAdvisor`. 20% de acurácia e mediana de $MTTDiag = 300\,\text{s}$.
  * **Nível 3 (Fragmented / Fragmentado):** Tem Prometheus, Loki e Jaeger em silos isolados sem vínculo semântico ($D_2 < 4$). Quando há falha em cascata, **erra 100% dos diagnósticos (0% de acurácia) devido ao *Cascading Span Bias*!**
  * **Nível 4 (Correlated - O PANOPTES):** Fusão semântica multimodal (M, L, T, E) com decomposição de *self-time* exclusivo ($T_{\text{self}}$). Diagnóstico em **17,27 segundos (mediana) com 83,33% de acurácia**.
  * **Nível 5 (Autonomous / Autônomo):** O horizonte futuro (AIOps em malha fechada com GNN/GAT, ponderação FinOps/GreenOps e *self-healing* autônomo).
* **Dica de fala:** *"O OMM é uma contribuição prescritiva avaliada empiricamente (Tipo 3 de Helgesson et al., 2012): ele substitui questionários subjetivos por 15 indicadores quantitativos declarativos (QCIs) e função stage-gate não-compensatória."*

---

### Slide 17: Visão Geral da Arquitetura PANOPTES
* **O que está na tela:** O diagrama arquitetural do PANOPTES em 4 camadas:
  1. *Coleta:* Sensores leves nos nós (OpenTelemetry Collector DaemonSet);
  2. *Normalização:* Enriquecimento semântico padronizado (`service.name`, `k8s.pod.name`, `trace_id`);
  3. *Armazenamento Especializado:* Cada dado no seu banco mais rápido e econômico (Prometheus pull, Loki index-by-label, Tempo index-free);
  4. *Correlação e RCA:* Visualização integrada (Grafana) e consultas programáticas correlacionadas (PromQL, LogQL, TraceQL).
* **A analogia:** Uma linha de montagem industrial de alta precisão. O sensor colhe o grão, a esteira padroniza os pacotes, armazena no silo correto e a central exibe o estoque em tempo real.

---

### Slide 18: Princípios de Controle (CPs) & Heurísticas de Contingência (ConHs)
* **O que está na tela:** As regras formais de *Design Knowledge* da arquitetura:
  * **CP1 (Vínculo Causal):** Vínculo contextual explícito entre métricas, logs e traces via identificadores W3C (`trace_id`) e *exemplars* em histogramas.
  * **CP2 (Representação Unificada do Estado):** Identidade dimensional canônica compartilhada entre sinais via convenções OTLP e metadados do Kubernetes.
  * **ConH1 (Controle Declarativo):** Automação e reconciliação de estado via IaC (Ansible/Helm) e Kubernetes Operators.
  * **ConH2 (Rejeição de Desvio / Configuration Drift):** Tratamento do desvio de configuração como perturbação externa a ser eliminada.
  * **ConH3 (Feedback Adaptativo / Bounded Overhead):** Proteção contra o *Efeito Observador* via batching OTel e armazenamento *index-free* ($\Delta_{\text{CPU}} \le 15\%$).
* **Dica de fala:** *"Esses princípios e heurísticas são o elo entre a teoria de controle e a engenharia de software, garantindo que o PANOPTES opere dentro de um envelope estrito de recursos."*

---

### Slide 19: Decisões Arquiteturais Registradas (MADR-0001 a MADR-0006)
* **O que está na tela:** Seis decisões arquiteturais e metodológicas documentadas no padrão formal *MADR* (protegendo a validade científica):
  * **ADR-0001:** Design fatorial pareado estratificado (`RANDOM_SEED = 42`; $11$ `cpu-stress`, $10$ `network-delay`, $9$ `pod-kill` em blocos $3 \times 4$) e simetria temporal de polling ($4\,\text{s}$);
  * **ADR-0002:** Eliminação de *data leakage* (operação 100% via APIs HTTP sem fallback `kubectl` no Cenário 4b, usando decomposição de *self-time* exclusivo $T_{\text{self}}$);
  * **ADR-0003:** Amostragem anti-pseudorreplicação a cada $16\,\text{s}$ (superando a janela de $15\,\text{s}$ do `metrics-server`, Hurlbert, 1984);
  * **ADR-0004:** Isolamento de alvo no Chaos Mesh (`direction: to` e binding exato ao pod para separar `cart` de `valkey-cart`);
  * **ADR-0005:** Ajuste de `inotify` no kernel e poda de 8 pods não-transacionais da demo OTel v3.1.0, evitando *thrashing* de swap (`kswapd0`);
  * **ADR-0006:** Evolução do substrato de virtualização (`Vagrant` $\rightarrow$ `Multipass` $\rightarrow$ `K3d` nativo no WSL2 com cotas rígidas de `cgroups`: $2.0\,\text{vCPU}$ e $4\,\text{GiB}$ RAM/nó).
* **A ideia simples:** Mostrar transparência e rastreabilidade científica. Cada ameaça à validade encontrada no ciclo de design gerou um registro formal auditável.

---

### Slide 20: Design Fatorial $2 \times 2$ & Ambiente Experimental
* **O que está na tela:** Como o experimento foi montado:
  * Dois fatores cruzados: Arquitetura (Vanilla K8s vs. PANOPTES) $\times$ Estado Operacional (Steady-State vs. Chaos Injection).
  * Quatro cenários resultantes (+ sub-regime exploratório):
    * **Cenário 1 (Vanilla Steady-State):** Linha de base de recursos sem agentes ($N=30$ amostras a cada $16\,\text{s}$).
    * **Cenário 2 (PANOPTES Steady-State):** Medição da sobrecarga de CPU e RAM da pilha PANOPTES ($H_{1,3}$).
    * **Cenário 3 e 3-Stratified (Vanilla Chaos):** Diagnóstico via CLI nativa (`kubectl get/logs/top`) sob $N=30$ falhas pareadas.
    * **Cenário 4a (Monomodal Trace RCA) e 4b (PANOPTES Multimodal RCA):** Diagnóstico sob as mesmas $N=30$ falhas pareadas ($H_{1,1}$ e $H_{1,2}$).
* **A analogia:** Como um ensaio clínico controlado e pareado: ambos os ambientes recebem exatamente a mesma sequência de 30 falhas geradas pela semente `RANDOM_SEED = 42`.

---

### Slide 21: Protocolo de Injeção de Falhas (Chaos Mesh)
* **O que está na tela:** As 3 classes de perturbações injetadas ($N=30$ ensaios pareados nos serviços `payment`, `cart`, `shipping` e `currency`):
  * **`cpu-stress` ($n=11$):** Saturação de 100% de CPU via `stress-ng` no cgroup do container por $180\,\text{s}$;
  * **`network-delay` ($n=10$):** Injeção de $2000\,\text{ms}$ ($\pm 100\,\text{ms}$ jitter, `direction: to`) via `tc-netem` no namespace de rede do pod;
  * **`pod-kill` ($n=9$):** Terminação abrupta do pod alvo, testando preservação forense de logs e métricas de reinicialização.
* **A ideia simples:** Provar que o PANOPTES foi avaliado sob falhas latentes (saturação silenciosa e atrasos em cascata) e falhas abruptas com teto de censura à direita em $300\,\text{s}$.

---

### Slide 22: O Viés de Duração em Cascata: Por que o Tracing Isolado Falhou?
* **O que está na tela:** Uma das maiores descobertas da tese explicada com clareza!
* **O mistério:** Por que o Cenário 4a (Tracing Monomodal isolado) teve **0% de acurácia ($0/30$, 100% de falsos positivos)**?
* **A descoberta:** O *Cascading Span Bias* (Viés de Duração em Cascata)!
  1. Um serviço de fundo (`cart` ou `currency`) sofre $2000\,\text{ms}$ de atraso.
  2. O `checkout` e o `frontend-proxy` ficam esperando a resposta síncrona.
  3. O *span* pai no `frontend-proxy` engloba a soma do tempo de todos os filhos ($T_{\text{parent}} \ge \sum T_{\text{children}}$).
  * Um algoritmo que ordena *spans* pela duração total inclusiva culpa sistematicamente o gateway de entrada (`frontend-proxy`) ou spans de GC de serviços de background (`ad`).
* **A solução do PANOPTES:** Calcular o **Self-Time Exclusivo** ($T_{\text{self}} = T_{\text{span}} - \sum T_{\text{children}}$), resolver os atributos de par L4/L7 (`server.address`, `net.peer.name`) e cruzar com saturação de CPU (PromQL) e logs de exceção (LogQL).
* **Dica de fala:** *"Demonstramos empiricamente que ferramentas de tracing isoladas (Nível 3 do OMM) sofrem do viés de duração em cascata, errando 100% dos diagnósticos. A decomposição de Self-Time acoplada à correlação multimodal (Nível 4) elimina esse viés."*

---

### Slide 23: Hipótese $H_{1,3}$: Sobrecarga de CPU no Workload
* **O que está na tela:** Distribuição de CPU mostrando que a pilha PANOPTES no namespace `monitoring` consumiu em média **$189{,}47\,\text{mCPU}$**, o que representa apenas **$9{,}51\% \pm 2{,}14\%$** (mediana **$8{,}83\%$**) do consumo de CPU do workload monitorado ($1{,}994{,}43\,\text{mCPU}$).
* **A validação:** Estritamente abaixo do teto operacional de $\theta_{\text{CPU}} = 15\%$ (Teste de Wilcoxon monocaudal: $W = 4{,}0, \; p = 6{,}52 \times 10^{-9}$).

---

### Slide 24: Hipótese $H_{1,3}$: Pegada de Memória RAM no Cluster
* **O que está na tela:** Distribuição de memória residente (RSS).
* **A explicação:** Enquanto coletores usam pouca memória, bancos de séries temporais e traces em memória mantêm um *working set* base fixo ($3{,}235{,}73\,\text{MiB}$). Graças à indexação apenas por labels do Loki e armazenamento sem índice do Tempo, toda a pilha ocupou **$26{,}33\% \pm 1{,}14\%$** da capacidade total de $12\,\text{GiB}$ do cluster.
* **Resultado:** Estritamente contido no envelope seguro de $\theta_{\text{RAM}} \le 30\%$ (Wilcoxon $W = 0{,}0, \; p = 9{,}31 \times 10^{-10}$), validando integralmente a Hipótese $H_{1,3}$.

---

### Slide 25: Hipótese $H_{1,1}$: Redução Massiva de Latência (MTTDiag)
* **O que está na tela:** Comparativo do Tempo para Diagnosticar (*MTTDiag*):
  * **Vanilla CLI (Cenário 3):** Mediana de **$300{,}00\,\text{s}$** (média de $242{,}42\,\text{s}$).
  * **PANOPTES (Cenário 4b):** Mediana de **$17{,}27\,\text{s}$** (média de $54{,}52\,\text{s}$).
* **A conclusão:** Redução de **$94{,}24\%$ na mediana** (e $-77{,}51\%$ na média), com Mann-Whitney $U = 165{,}0$ ($p = 4{,}55 \times 10^{-6}$), Wilcoxon pareado $W = 27{,}0$ ($p = 3{,}06 \times 10^{-5}$) e tamanho de efeito grande de Vargha-Delaney ($\hat{A}_{12} = 0{,}8167$). Hipótese $H_{1,1}$ validada!

---

### Slide 26: Hipótese $H_{1,2}$: Superioridade em Acurácia Diagnóstica (Acc)
* **O que está na tela:** Desempenho estratificado por classe de falha:
  * `cpu-stress` ($n=11$): Vanilla **$0{,}0\%$ ($0/11$)** | Tracing **$0{,}0\%$ ($0/11$)** | PANOPTES **$100{,}0\%$ ($11/11$)**.
  * `pod-kill` ($n=9$): Vanilla **$33{,}3\%$ ($3/9$)** | Tracing **$0{,}0\%$ ($0/9$)** | PANOPTES **$100{,}0\%$ ($9/9$)**.
  * `network-delay` ($n=10$): Vanilla **$30{,}0\%$ ($3/10$)** | Tracing **$0{,}0\%$ ($0/10$)** | PANOPTES **$50{,}0\%$ ($5/10$)**.
  * **Global ($N=30$):** Vanilla **$20{,}00\%$ ($6/30$)** (e $23{,}33\%$ na replicação S3-Strat) vs. Tracing **$0{,}00\%$ ($0/30$)** vs. PANOPTES **$83{,}33\%$ ($25/30$)** (Teste Exato de Fisher $\text{OR} = 20{,}0, \; p = 7{,}74 \times 10^{-7}$; McNemar pareado $p = 7{,}83 \times 10^{-5}$). Hipótese $H_{1,2}$ validada!

---

### Slide 27: Análise de Sobrevivência e Censura (Curvas de Kaplan-Meier)
* **O que está na tela:** Curva de sobrevivência de Kaplan-Meier modelando a probabilidade $P(T > t)$ de uma falha permanecer sem diagnóstico correto ao longo da janela de $300\,\text{s}$.
* **O resultado:** Enquanto os baselines Vanilla sofrem **$73{,}33\%$ a $80{,}00\%$ de censura à direita** (totalmente cegos a `cpu-stress` e a atrasos gRPC), a curva do PANOPTES cai abruptamente nos primeiros $36\,\text{s}$ (Teste Log-Rank $\chi^2 = 23{,}36, \; p = 1{,}34 \times 10^{-6}$).
* **Dica de fala:** *"A modelagem de sobrevivência de Kaplan-Meier comprova estatisticamente a aceleração temporal da convergência diagnóstica sob o PANOPTES frente ao teto operacional de 300 segundos."*

---

### Slide 28: Ameaças à Validade & Estratégias de Mitigação
* **O que está na tela:** Os cuidados metodológicos para garantir que o resultado não foi "sorte" ou "ambiente viciado" (baseado em Wohlin et al., 2012):
  * *Validade de Conclusão:* Testes estatísticos rigorosos (Shapiro-Wilk, Mann-Whitney);
  * *Validade Interna:* Sementes fixas para que o experimento seja 100% repetível em qualquer computador do mundo;
  * *Validade de Construto:* Uso de métricas padronizadas da indústria ($MTTDiag$, Acurácia);
  * *Validade Externa:* Testado usando uma loja virtual de microsserviços real mantida pelo consórcio CNCF (*CNCF Astronomy Shop* / *OpenTelemetry Demo*).

---

### Slide 29: Síntese das Contribuições da Tese (1/2: Arquitetura & Artefato)
* **O que está na tela:** As três primeiras grandes entregas consolidadas:
  1. A arquitetura de referência PANOPTES implementada e funcionando;
  2. Os Princípios de Controle e Heurísticas formais (CP1, CP2, ConH1 a ConH3);
  3. A automação completa por Infraestrutura como Código (Helm e Ansible), permitindo que qualquer pessoa suba o cluster com um único comando.

---

### Slide 30: Síntese das Contribuições da Tese (2/2: Evidência & Maturidade)
* **O que está na tela:** As outras grandes entregas consolidadas:
  3. O Benchmark Empírico sob Chaos Engineering (comprovando o colapso do tracing isolado com 0% de acurácia e a eficácia da correlação multimodal com 83,33% de acurácia e mediana de 17,27 s);
  4. O Modelo de Maturidade de Observabilidade (OMM) de 5 níveis e 5 dimensões (15 QCIs).

---

### Slide 31: Produção Científica & Artigos Derivados da Tese
* **O que está na tela:** O mapeamento dos 4 manuscritos derivados da tese (Etapa 6 da DSRM — Comunicação), com escopos empíricos desacoplados:
  1. **Artigo 1 (CN-OMM):** Modelo de Maturidade Prescritivo $5\times 5$ (15 QCIs), auditoria programática de 5 perfis (`L1`–`L5`) e *Maturity Overestimation Gap* ($\Delta_{\text{inflate}} = +0{,}93$) — alvo: *IST / JSS*;
  2. **Artigo 2 (PANOPTES Reference Architecture):** Arquitetura em 4 camadas, Princípios de Controle (`CP1`/`CP2`), 6 MADRs, verificação de mecanismos por subsistema e pegada de recursos por camada — alvo: *JSS / FGCS*;
  3. **Artigo 3 (Multimodal Observability in Chaos Engineering):** Experimento controlado em duas fases ($N=30$ pareado), prova do *Cascading Span Bias* ($0\%$ acc), decomposição de *Self-Time* ($83{,}3\%$ acc) e curvas de Kaplan-Meier — alvo: *EMSE*;
  4. **Artigo 4 (Chaos Engineering in Action):** Benchmark empírico pareado ($N=60$) comparando mecanismos de injeção de falhas no kernel Linux (Chaos Mesh vs. LitmusChaos) — alvo: *SPE / IEEE IC*.

---

### Slide 32: Roadmap de Extensões até a Defesa Final
* **O que está na tela:** Quatro passos planejados em cascata até a Defesa Final do Doutorado:
  1. **Validação Externa em Nuvem Pública (Google Cloud / GKE):** Provisionamento via Terraform sob CNI de nuvem real e variabilidade de rede;
  2. **Refinamento de Detecção Sub-Limiar & Exemplars ($p95/p99$):** Vínculo direto entre histogramas Prometheus e traces do Tempo em rotas esparsas;
  3. **Telemetria Zero-Code com eBPF no Kernel (Beyla / Cilium):** Sondas no kernel Linux para capturar latências de socket e retransmissões TCP sem alterar código;
  4. **Fechamento do Ciclo Autonômico de Controle (OMM Nível 5):** Acoplamento do motor de RCA a um Kubernetes Operator para autocura (*self-healing*) em malha fechada.

---

### Slide 33: Cronograma até a Defesa Final
* **O que está na tela:** Tabela temporal dividida em 4 fases (Meses 1 a 6 pós-qualificação):
  * Fase 1 (Meses 1–2): Recomendações da banca e campanha em nuvem pública (GKE via Terraform);
  * Fase 2 (Mês 3): Análise comparativa cruzada (K3d local vs. GKE Cloud) e refinamento dos algoritmos de latência;
  * Fase 3 (Mês 4): Submissão e acompanhamento editorial dos 4 artigos derivados da tese (*IST*, *JSS*, *EMSE*, *SPE*);
  * Fase 4 (Meses 5–6): Revisão final da tese, pacote de replicação open-source e Defesa Final de Doutorado.

---

### Slide 34: Agradecimentos e Encerramento
* **O que está na tela:** Mensagem de agradecimento aos professores avaliadores, orientadores, CIn-UFPE e sessão de perguntas e discussão.
* **Dica de fala:** *"Agradeço profundamente aos professores da banca pelas contribuições e pelo tempo dedicado a esta avaliação. Estou à inteira disposição para responder às perguntas e aprofundar qualquer aspecto técnico ou metodológico da pesquisa."*

---

## 4. As Principais Descobertas Científicas ("O Ouro da Tese")

Se alguém lhe perguntar na rua ou na banca: *"Qual é a real novidade científica desse trabalho?"*, a resposta se resume a três pilares:

1. **A Descoberta do Viés de Duração do Tracing (Self-Time):**
   Descobrimos matematicamente por que as ferramentas de tracing isoladas falham em falhas em cascata: elas apontam para quem ficou esperando mais tempo (o topo da cascata) em vez de apontar para quem travou de verdade (o fundo da cascata). O PANOPTES resolve isso calculando o *Self-Time* exclusivo.
2. **A Prova de que Correlação Multimodal Reduz 94,24% da Mediana de Latência Diagnóstica (77,51% na Média):**
   Não basta ter gráficos bonitos. Quando você conecta métricas com logs e traces pelo mesmo identificador, a mediana do tempo de diagnóstico despenca de 300 segundos para 17,27 segundos, com acurácia de 83,33%.
3. **O Modelo de Maturidade (OMM) Formalizado:**
   Criamos uma régua científica de 5 níveis baseada na literatura que ensina como sair do caos de comandos de terminal (Nível 2) até a observabilidade preditiva autônoma (Nível 5).

---

## 5. Possíveis Perguntas da Banca e Como Responder

### Pergunta 1: *"Por que você usou o K3d e não um cluster Kubernetes gerenciado na AWS (EKS) ou Google (GKE)?"*
* **Como responder:**
  > *"Excelente pergunta, professor. No método de Engenharia de Software Experimental, o primeiro ciclo de validação de um artefato exige **rigor e controle estrito de variáveis intervenientes**. Nuvens públicas como AWS introduzem 'ruídos de vizinho' (*noisy neighbors*), latências imprevisíveis de hipervisor e falta de controle sobre os cgroups do kernel. O K3d em nó dedicado com WSL2 nos deu isolamento cirúrgico de CPU e memória, com sementes determinísticas que tornam o experimento 100% reproduzível por qualquer outro pesquisador. A validação em nuvem pública (AWS/GKE) já está formalizada como o quarto passo do nosso Roadmap de Extensões até a defesa final."*

### Pergunta 2: *"Qual a diferença entre a sua arquitetura e simplesmente instalar a stack LGTM (Loki, Grafana, Tempo, Mimir) pronta?"*
* **Como responder:**
  > *"A stack LGTM tradicional disponibiliza os componentes isolados, mas não impõe um modelo de dados canônico nem políticas automáticas de correlação semântica. Se um desenvolvedor apenas instalar o LGTM, ele continuará sofrendo com o viés de duração em cascata e com silos de metadados. O PANOPTES não é uma mera coleção de softwares: ele é uma **arquitetura de referência fundamentada em Princípios de Controle (CP1 e CP2)** e **Heurísticas formais (ConH1 a ConH3)** que realiza a decomposição de Self-Time e correlaciona automaticamente os atributos de recursos OTLP em tempo finito."*

### Pergunta 3: *"Por que o Teorema de Kalman de 1959 se aplica a software moderno?"*
* **Como responder:**
  > *"Porque um cluster de microsserviços é, em sua essência, um sistema dinâmico de múltiplas entradas e múltiplas saídas (MIMO). Kalman demonstrou que um sistema só é observável se o seu estado interno $x(t)$ pode ser determinado a partir de suas saídas mensuráveis $y(t)$. Historicamente, a computação chamava 'monitoramento' de observabilidade. Nós resgatamos Kalman para mostrar que olhar para alertas estáticos (CPU alta) é apenas monitoramento sintomático. A verdadeira observabilidade kalmaniana exige reconstruir a dinâmica interna (o caminho e as causas das falhas latentes) a partir da tupla rica de telemetria $\mathcal{O} = \{M, L, T, E\}$."*

---
*Documento elaborado como material de apoio pedagógico e preparação para o Exame de Qualificação de Doutorado.*
