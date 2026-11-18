# Apresentação de Qualificação de Doutorado (LaTeX Beamer)

Este diretório contém a apresentação de slides para o **Exame de Qualificação de Doutorado** de **Fagner Fernandes Candido da Silva** no Programa de Pós-Graduação em Ciência da Computação (PPGCC) do Centro de Informática (CIn) da Universidade Federal de Pernambuco (UFPE).

**Título da Tese:** *PANOPTES: An Open-Source Reference Architecture for Observability in Kubernetes Ecosystems*  
**Orientador:** Prof. Dr. Vinícius Cardoso Garcia  
**Coorientador:** Prof. Dr. Jackson Raniel Florêncio da Silva  
**Área de Concentração:** Engenharia de Software e Linguagens de Programação  

---

## 📂 Arquivos

- `main_presentation.tex`: Código-fonte completo em LaTeX Beamer (proporção widescreen 16:9, paleta visual oficial do **Manual de Identidade Visual CIn-UFPE - Ago. 2020**).
  - **Vermelho CIn (Primária):** `#DB1E2F` (RGB: 219, 30, 47 | Pantone 1795 C)
  - **Vermelho Escuro (Secundária):** `#AF0421` (RGB: 175, 4, 33 | Pantone 200 C)
  - **Preto Institucional:** `#231F20` (RGB: 35, 31, 32 | Pantone 419 C)
  - **Cinza Claro:** `#E0E1E0` (RGB: 224, 225, 224 | Pantone 664 C)
  - **Logo Oficial:** `HC.png` (Horizontal Colorida).
- `main_presentation.pdf`: Apresentação compilada em PDF pronta para exibição.
- `compile.sh`: Script automatizado para compilar os slides utilizando a imagem Docker oficial do projeto (`texlive/texlive:TL2021-historic`).

---

## 🚀 Como Compilar

### Opção 1: Via Script Docker (Recomendado)

Na pasta `presentation`, execute:

```bash
./compile.sh
```

### Opção 2: Via Docker Diretamente

```bash
docker run --rm \
  -v "$(pwd)/..:/workdir" \
  -w /workdir/presentation \
  texlive/texlive:TL2021-historic \
  pdflatex -interaction=nonstopmode main_presentation.tex
```

### Opção 3: No VS Code (LaTeX Workshop) ou Overleaf

Abra o arquivo `main_presentation.tex` diretamente no VS Code com a extensão LaTeX Workshop ou importe a pasta no Overleaf.

---

## 📑 Estrutura dos Slides (34 Frames)

1. **Slide 1**: Capa Institucional (CIn-UFPE, PPGCC, título, candidato e orientadores).
2. **Slide 2**: Agenda da Apresentação.
3. **Slides 3--8 (Seção 1)**: Contexto Cloud-Native, Conceito Canônico de Kalman (1959), Mapeamento de Variáveis de Estado, Limitações do Kubernetes Vanilla, Ecossistema CNCF e Missão do PANOPTES.
4. **Slides 9--11 (Seção 2)**: Perguntas de Pesquisa (MRQ + SRQ1--SRQ4), Objetivos (Geral + SO1--SO4) e Hipóteses Formais ($H_{1,1}$, $H_{1,2}$, $H_{1,3}$).
5. **Slides 12--16 (Seção 3)**: Metodologia DSRM (Peffers et al., 2006), Três Ciclos de Hevner (2004), Protocolo PRISMA da Rapid Review ($312 \rightarrow 10$), Lacuna de Validação (Wendler, 2012) e Modelo de Maturidade OMM ($5 \times 5$, 15 QCIs, agregação *stage-gate* e níveis L1--L5).
6. **Slides 17--19 (Seção 4)**: A Arquitetura de Referência PANOPTES em 4 camadas, Princípios de Controle (CP1, CP2), Heurísticas de Contingência (ConH1--ConH3) e Registros de Decisão Arquitetural (ADR-0001 a ADR-0006).
7. **Slides 20--22 (Seção 5)**: Design Fatorial $2 \times 2$, Testbed K3d multi-node com cgroups, Protocolo de Injeção de Falhas (Chaos Mesh, `RANDOM_SEED=42`) e o Viés de Duração em Cascata (decomposição de *Self-Time* $T_{\text{self}}$).
8. **Slides 23--27 (Seção 6)**: Validação Empírica das Hipóteses:
   - $H_{1,3}$ (Sobrecarga de CPU em $9.51\% \pm 2.14\%$ e RAM em $26.33\% \pm 1.14\%$, $p < 10^{-8}$);
   - $H_{1,1}$ (Redução de $94.24\%$ na mediana do $MTTDiag$, de $300.00\,\text{s}$ para $17.27\,\text{s}$, $p = 4.55 \times 10^{-6}$, $\hat{A}_{12}=0.8167$);
   - $H_{1,2}$ (Acurácia de $83.33\%$ vs $20.00\%$ no Vanilla S3, $23.33\%$ no S3-Strat e $0.00\%$ no Tracing-only S4a, $p = 7.74 \times 10^{-7}$);
   - Análise de Sobrevivência de Kaplan-Meier e Censura à Direita (Log-Rank $p = 1.34 \times 10^{-6}$).
9. **Slides 28--31 (Seção 7)**: Ameaças à Validade (Interna, Construto, Conclusão, Externa), Síntese das Contribuições da Tese (1/2 e 2/2) e Produção Científica & Artigos Derivados da Tese (Artigos 1 a 4 desacoplados).
10. **Slides 32--33 (Seção 8)**: Roadmap Pós-Qualificação (extensão GKE com Terraform, Exemplars $p95/p99$, eBPF/Beyla, OMM L5 self-healing) e Cronograma até a Defesa Final.
11. **Slide 34**: Conclusão, Agradecimentos e Sessão de Perguntas.
