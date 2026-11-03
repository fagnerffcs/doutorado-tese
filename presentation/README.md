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

## 📑 Estrutura dos Slides (24 Frames)

1. **Slide 1**: Capa Institucional (CIn-UFPE, PPGCC, título, candidato e orientadores).
2. **Slide 2**: Agenda da Apresentação.
3. **Slides 3--5 (Parte I)**: Contexto Cloud-Native, Dualidade de Controle de Kalman (1959) e Limitações do Kubernetes Vanilla.
4. **Slides 6--7 (Parte II)**: Perguntas de Pesquisa (MRQ + SRQ1--SRQ4), Objetivos e Hipóteses ($H_{1,1}$, $H_{1,2}$, $H_{1,3}$).
5. **Slides 8--9 (Parte III)**: Metodologia Dual (DSRM + Rapid Review) e o Modelo de Maturidade OMM (Níveis L1--L5).
6. **Slides 10--12 (Parte IV)**: A Arquitetura de Referência PANOPTES, Princípios de Controle (CP1, CP2), Heurísticas (ConH1--ConH3) e Registros de Decisão Arquitetural (ADR-0001 a ADR-0006).
7. **Slides 13--15 (Parte V)**: Design Fatorial $2 \times 2$, Testbed K3d multi-node com cgroups, Injeção de Falhas (Chaos Mesh) e o Viés de Duração em Cascata (por que o tracing isolado colapsou com 0% acc).
8. **Slides 16--19 (Parte VI)**: Validação Empírica das Hipóteses:
   - $H_{1,3}$ (Sobrecarga de CPU e RAM estritamente delimitadas, $p < 10^{-8}$);
   - $H_{1,1}$ (Redução de $94.24\%$ no $MTTDiag$, de $300\,\text{s}$ para $17.27\,\text{s}$, $p = 4.55 \times 10^{-6}$);
   - $H_{1,2}$ (Acurácia de $83.33\%$ vs $20.00\%$ no Vanilla e $0.00\%$ no Tracing-only, $p = 7.74 \times 10^{-7}$);
   - Análise de Sobrevivência de Kaplan-Meier e Censura à Direita.
9. **Slides 20--21 (Parte VII)**: Ameaças à Validade (Interna, Construto, Conclusão, Externa) e Síntese das Contribuições da Tese.
10. **Slides 22--23 (Parte VIII)**: Roadmap Pós-Qualificação (extensão GKE com Terraform, eBPF/Beyla, OMM L5 self-healing) e Cronograma até a Defesa Final.
11. **Slide 24**: Conclusão, Agradecimentos e Sessão de Perguntas.
