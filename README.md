# Local LaTeX Compilation with Docker & VS Code

Este projeto está configurado para ser compilado localmente utilizando um container Docker com a imagem do TeX Live 2021 (texlive/texlive:TL2021-historic). Essa abordagem garante que o projeto seja compilado exatamente com as mesmas dependências e versões de pacotes, independentemente do sistema operacional do usuário, sem a necessidade de instalar uma distribuição LaTeX pesada (como TeX Live ou MiKTeX) diretamente na máquina.

## 🛠️ Pré-requisitos

Antes de começar, certifique-se de ter os seguintes softwares instalados em sua máquina:

- Visual Studio Code (VS Code)
- Docker Desktop (O serviço do Docker precisa estar em execução)
- Extensão do VS Code: LaTeX Workshop

## ⚙️ Configuração do VS Code

Para instruir a extensão LaTeX Workshop a usar o Docker em vez de uma instalação local do LaTeX, você precisa adicionar as configurações abaixo ao arquivo settings.json do seu projeto.

Na raiz do projeto, crie uma pasta chamada .vscode (caso não exista).

Dentro dessa pasta, crie um arquivo chamado settings.json.

Copie e cole o seguinte código:

```JSON
{
    "latex-workshop.latex.outDir": "%DIR%/output",
    "latex-workshop.latex.tools": [
        {
            "name": "docker-latexmk-2021",
            "command": "docker",
            "args": [
                "run",
                "--rm",
                "-v",
                "%DIR%:/workdir",
                "-w",
                "/workdir",
                "texlive/texlive:TL2021-historic",
                "latexmk",
                "-pdf",
                "-shell-escape", 
                "-synctex=1",
                "-interaction=errorstopmode", 
                "-file-line-error",
                "-outdir=output",
                "%DOCFILE%"
            ],
            "env": {}
        }
    ],
    "latex-workshop.latex.recipes": [
        {
            "name": "Docker 2021 Compile",
            "tools": [
                "docker-latexmk-2021"
            ]
        }
    ],
    "latex-workshop.latex.clean.command": "docker",
    "latex-workshop.latex.clean.args": [
        "run",
        "--rm",
        "-v",
        "%DIR%:/workdir",
        "-w",
        "/workdir",
        "texlive/texlive:TL2021-historic",
        "latexmk",
        "-c",
        "-outdir=output",
        "%DOCFILE%"
    ]
}
```

## O que essa configuração faz?

- outDir: Redireciona todos os arquivos gerados durante a compilação (incluindo o .pdf e arquivos auxiliares .aux, .log) para a pasta output/, mantendo a raiz do seu projeto limpa.

- tools & recipes: Cria uma "ferramenta" que chama o docker run, mapeando o diretório atual (%DIR%) para dentro do container (/workdir). Em seguida, executa o latexmk para compilar o arquivo principal.

- clean: Configura o comando de limpeza de arquivos temporários para também rodar através do container Docker.

## 🚀 Como Compilar o Projeto

Com as configurações salvas e o Docker rodando em segundo plano:

1. Abra o arquivo principal do projeto (ex: main.tex).

2. Abra a Paleta de Comandos do VS Code (Ctrl + Shift + P no Windows/Linux ou Cmd + Shift + P no Mac).

3. Digite e selecione: LaTeX Workshop: Build with recipe.

4. Escolha a receita Docker 2021 Compile.

Dica: Na primeira execução, o Docker fará o download da imagem texlive/texlive:TL2021-historic (cerca de alguns gigabytes), o que pode demorar alguns minutos. Nas próximas vezes, a compilação será imediata.

## 🧹 Como Limpar Arquivos Auxiliares

Caso ocorra algum erro fatal (como corrompimento de bibliografia no bbl/aux) e o projeto pare de compilar, você pode limpar os arquivos temporários:

Abra a Paleta de Comandos (Ctrl + Shift + P).

Digite e selecione: LaTeX Workshop: Clean up auxiliary files.

Recompile o projeto do zero.