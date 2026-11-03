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
   - [Slide 31: Roadmap de Extensões até a Defesa Final](#slide-31-roadmap-de-extensões-até-a-defesa-final)
   - [Slide 32: Cronograma até a Defesa Final](#slide-32-cronograma-até-a-defesa-final)
   - [Slide 33: Agradecimentos e Encerramento](#slide-33-agradecimentos-e-encerramento)
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
  * $H_{1,3}$: O consumo de CPU ($\le 10\%$) e RAM ($\le 8\%$) da própria observabilidade será baixo e seguro.
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
* **O que está na tela:** Uma escada de 5 degraus que permite a qualquer empresa saber em que nível ela está:
  * **Nível 1 (Inexistente):** Ninguém mede nada. O cliente no Twitter é quem avisa que o sistema caiu.
  * **Nível 2 (Inicial / Terminal):** Engenheiros entram no terminal preto na hora do desespero. 20% de acurácia.
  * **Nível 3 (Silos Isolados):** Tem Prometheus e Jaeger, mas eles não se conversam. Quando há falha em cascata, **erra 100% dos diagnósticos (0% de acurácia)!**
  * **Nível 4 (Otimizado - O PANOPTES):** Métricas, logs e traces correlacionados. Diagnóstico em **17 segundos com 83,3% de acurácia**.
  * **Nível 5 (Autonômico):** O futuro (o sistema prevê a falha e se conserta sozinho).
* **Dica de fala:** *"O OMM é uma contribuição prescritiva: ele serve tanto como régua diagnóstica para a indústria quanto como mapa de evolução para a engenharia de software."*

---

### Slide 17: Visão Geral da Arquitetura PANOPTES
* **O que está na tela:** O diagrama arquitetural do PANOPTES em 4 camadas:
  1. *Coleta:* Sensores leves nos nós (OpenTelemetry Collector);
  2. *Agregação:* Padronização de nomes e identificadores;
  3. *Armazenamento Especializado:* Cada dado no seu banco mais rápido e barato (Prometheus, Loki, Tempo);
  4. *Correlação e Telas:* O correlacionador que une as pontas e desenha no Grafana.
* **A analogia:** Uma linha de montagem industrial de alta precisão. O sensor colhe o grão, a esteira padroniza os pacotes, armazena no silo correto e a central exibe o estoque em tempo real.

---

### Slide 18: Princípios de Controle (CPs) & Heurísticas de Contingência (ConHs)
* **O que está na tela:** As regras de ouro formais da arquitetura:
  * **CP1 (Vinculação Causal):** Nenhum log ou métrica pode nascer sem um carimbo de identidade que o conecte a uma requisição.
  * **CP2 (Estado Unificado):** Todos os sinais devem convergir para a mesma linha temporal.
  * **ConH1 (Decomposição de Self-Time):** Descontar o tempo dos filhos para descobrir o verdadeiro culpado.
  * **ConH2 (Triangulação Multimodal):** Nunca confie em apenas um sinal; cruze o número (métrica), o texto (log) e o caminho (trace).
  * **ConH3 (Proteção de Recursos):** O observador não pode gastar a energia do observado.
* **Dica de fala:** *"Esses princípios e heurísticas são o elo entre a teoria de controle e a engenharia de software, garantindo que o PANOPTES tome decisões diagnósticas determinísticas."*

---

### Slide 19: Decisões Arquiteturais Registradas (MADR-0001 a MADR-0006)
* **O que está na tela:** Seis decisões de projeto documentadas no padrão formal *MADR*:
  * MADR-0001: Usar OpenTelemetry (para não ficar preso a empresas proprietárias);
  * MADR-0002: Usar Loki (guarda logs compactados por blocos, sendo 10x mais leve que Elasticsearch);
  * MADR-0003: Usar Grafana Tempo para traces sem indexação pesada;
  * MADR-0004: Injetar falhas usando Chaos Mesh;
  * MADR-0005: Automação 100% por código (Ansible e Helm);
  * MADR-0006: Uso de cluster K3d com isolamento de recursos via cgroups.
* **A ideia simples:** Mostrar transparência científica. Nenhuma escolha tecnológica foi por "gosto pessoal"; todas tiveram justificativa técnica e foram documentadas para permitir replicação exata.

---

### Slide 20: Design Fatorial $2 \times 2$ & Ambiente Experimental
* **O que está na tela:** Como o experimento foi montado:
  * Dois fatores testados: Com/Sem Instrumentação Avançada $\times$ Com/Sem Injeção de Falhas.
  * Quatro cenários resultantes:
    * Cenário 1: Sistema em dia de sol (sem falhas, sem carga).
    * Cenário 2: Sobrecarga normal de clientes.
    * Cenário 3: O teste de fogo (injeção de falhas em cascata).
    * Cenário 4: Teste de estresse prolongado para ver estabilidade.
* **A analogia:** Como um teste clínico de vacina: um grupo toma placebo, outro toma o remédio, um grupo é exposto ao vírus e outro não. Só assim a ciência tem certeza de que o remédio funciona.

---

### Slide 21: Protocolo de Injeção de Falhas (Chaos Mesh)
* **O que está na tela:** Como causamos problemas no cluster de forma científica:
  * Torrar a CPU de propósito (*CPU Burn*);
  * Vazar memória até quase travar (*Memory Stress*);
  * Injetar 200 ms de lentidão e perda de pacotes na rede (*Network Latency*);
  * Matar contêineres repentinamente (*Pod Kill*).
* **A ideia simples:** Provar que o PANOPTES não foi testado apenas em situações fáceis, mas sob estresse brutal semelhante aos piores dias de uma Black Friday.

---

### Slide 22: O Viés de Duração em Cascata: Por que o Tracing Isolado Falhou?
* **O que está na tela:** Uma das maiores descobertas da tese explicada com clareza!
* **O mistério:** Por que empresas gastam milhões com ferramentas de rastreamento (*tracing*) e continuam demorando horas para resolver problemas?
* **A descoberta:** O efeito dominó!
  1. O banco de dados trava.
  2. O serviço de pagamento fica esperando o banco.
  3. O serviço de checkout fica esperando o pagamento.
  4. O frontend (site) fica esperando o checkout e demora 5 segundos.
  * O gráfico tradicional de trace mostra a barra do frontend gigante (5 segundos). O operador humano ou um robô burro acha que o problema está no frontend!
* **A solução do PANOPTES:** Calcular o **Self-Time**. O frontend demorou 5 segundos, mas 4,9 segundos foram apenas esperando os outros; o seu *tempo próprio* foi de apenas 0,1s. O banco de dados, por outro lado, teve 4,5 segundos de trabalho travado nele mesmo. O PANOPTES expõe o verdadeiro vilão na hora!
* **Dica de fala:** *"Esta é uma das contribuições mais elegantes da tese: demonstramos que ferramentas de tracing isoladas sofrem do 'viés de duração em cascata', induzindo operadores a falsos positivos. O cálculo de Self-Time decompõe a árvore e isola o causador real."*

---

### Slide 23: Hipótese $H_{1,3}$: Sobrecarga de CPU no Workload
* **O que está na tela:** Gráfico de consumo de processador (CPU) mostrando que colocar o PANOPTES para vigiar o cluster consumiu menos de **4,8%** a mais de CPU.
* **A validação:** Nosso limite aceitável de segurança era de até 10%. Como gastamos menos da metade disso, a hipótese $H_{1,3}$ foi plenamente comprovada no quesito CPU.

---

### Slide 24: Hipótese $H_{1,3}$: Pegada de Memória RAM no Cluster
* **O que está na tela:** Gráfico de consumo de memória RAM.
* **A explicação:** Ferramentas antigas (como Elasticsearch) guardavam um dicionário gigante de cada palavra de cada log, devorando dezenas de gigabytes de RAM. O PANOPTES usa o Grafana Loki, que compacta os logs brutos e só indexa etiquetas essenciais.
* **Resultado:** O consumo de memória foi mínimo e previsível, completando a validação total da hipótese $H_{1,3}$.

---

### Slide 25: Hipótese $H_{1,1}$: Redução Massiva de Latência (MTTDiag)
* **O que está na tela:** Gráfico comparativo do Tempo Médio para Diagnosticar (*MTTDiag*):
  * No método manual (terminal): mais de **180 segundos** (3 minutos).
  * Com ferramentas em silos isolados: cerca de **110 segundos**.
  * Com o PANOPTES: apenas **17 segundos!**
* **A conclusão:** Redução de **85%** no tempo de diagnóstico com comprovação estatística irrefutável ($p < 0{,}001$). Hipótese $H_{1,1}$ validada!

---

### Slide 26: Hipótese $H_{1,2}$: Superioridade em Acurácia Diagnóstica (Acc)
* **O que está na tela:** Gráfico comparando a precisão do diagnóstico:
  * Quando ocorre uma falha simples, as ferramentas comuns até acertam. Mas quando ocorre uma falha em cascata complexa, **as ferramentas isoladas têm 0% de acurácia** (por causa da armadilha do viés de duração).
  * O PANOPTES atingiu **83,3% de acurácia determinística**. Hipótese $H_{1,2}$ comprovada!

---

### Slide 27: Análise de Sobrevivência e Censura (Curvas de Kaplan-Meier)
* **O que está na tela:** Um gráfico clássico da medicina (*curva de sobrevivência de Kaplan-Meier*).
* **Como a medicina usa isso:** Para medir quanto tempo um paciente sobrevive após iniciar um tratamento contra uma doença.
* **Como usamos isso na computação:** Quanto tempo uma *anomalia/defeito* sobrevive no cluster antes que alguém descubra a causa-raiz?
  * Na curva do PANOPTES, a linha despenca para zero quase imediatamente: nenhuma falha consegue "sobreviver" oculta por mais de alguns segundos.
  * No método tradicional, a linha continua alta por minutos, e muitas falhas são "censuradas" (o tempo limite de 5 minutos acaba e os engenheiros desistem sem descobrir a causa).
* **Dica de fala:** *"Importamos a modelagem de sobrevivência de Kaplan-Meier da bioestatística para provar a probabilidade temporal de retenção de anomalias: sob o PANOPTES, 100% dos incidentes são resolvidos antes que qualquer degradação se torne crônica."*

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
* **O que está na tela:** As outras três grandes entregas:
  4. O Modelo de Maturidade de Observabilidade (OMM) de 5 níveis;
  5. O protocolo de testes experimentais com Chaos Engineering;
  6. Produção bibliográfica: artigos em congressos/periódicos e registro público das decisões arquiteturais (MADRs).

---

### Slide 31: Roadmap de Extensões até a Defesa Final
* **O que está na tela:** Quatro passos planejados em cascata para os próximos meses até o dia da Defesa Final do Doutorado:
  1. **Coleta de Telemetria sem Código via eBPF:** Ler dados direto do núcleo (kernel) do sistema operacional, sem precisar mexer em uma linha sequer de código do desenvolvedor.
  2. **Amostragem Inteligente com IA:** Usar aprendizado de máquina para descartar dados repetidos e economizar espaço em disco.
  3. **Auto-Remediação Autonômica (OMM Nível 5):** O sistema não apenas descobre o erro, mas aplica o conserto sozinho em tempo real.
  4. **Validação em Nuvens Públicas:** Rodar os testes na AWS ou Google Cloud em escala de produção real.

---

### Slide 32: Cronograma até a Defesa Final
* **O que está na tela:** Uma tabela temporal dividindo os meses de 2026 e 2027:
  * Implementação do eBPF e da amostragem inteligente;
  * Condução da nova rodada de experimentos;
  * Escrita e submissão de artigo para revista Qualis A1/A2;
  * Escrita da versão final da tese;
  * Defesa Final de Doutorado.
* **A ideia simples:** Mostrar à banca que o cronograma é realista, bem planejado e totalmente viável.

---

### Slide 33: Agradecimentos e Encerramento
* **O que está na tela:** Mensagem de agradecimento aos professores avaliadores, orientadores, CIn-UFPE, órgãos de fomento (FACEPE/CAPES/CNPq) e links públicos do projeto no GitHub.
* **Dica de fala:** *"Agradeço profundamente aos professores da banca pelas contribuições e pelo tempo dedicado a esta avaliação. Estou à inteira disposição para responder às perguntas e aprofundar qualquer aspecto técnico ou metodológico da pesquisa."*

---

## 4. As Principais Descobertas Científicas ("O Ouro da Tese")

Se alguém lhe perguntar na rua ou na banca: *"Qual é a real novidade científica desse trabalho?"*, a resposta se resume a três pilares:

1. **A Descoberta do Viés de Duração do Tracing (Self-Time):**
   Descobrimos matematicamente por que as ferramentas de tracing isoladas falham em falhas em cascata: elas apontam para quem ficou esperando mais tempo (o topo da cascata) em vez de apontar para quem travou de verdade (o fundo da cascata). O PANOPTES resolve isso calculando o *Self-Time* exclusivo.
2. **A Prova de que Correlação Multimodal Reduz 85% do Tempo:**
   Não basta ter gráficos bonitos. Quando você conecta métricas com logs e traces pelo mesmo identificador, o tempo de diagnóstico despenca de mais de 3 minutos para 17 segundos, com acurácia de 83,3%.
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
