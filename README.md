# Formulário de Assessment de Operações Cloud

Este é um aplicativo web simples construído com Flask que apresenta um formulário de assessment para operações cloud. Ele permite aos usuários responderem a um conjunto de perguntas divididas em categorias, calcula as pontuações e exibe os resultados em um gráfico de radar.

## Funcionalidades

*   Formulário com perguntas divididas em 5 categorias: Arquitetura, Resiliência, Cyber Segurança, Governança e FinOps.
*   Cada pergunta tem um peso associado.
*   As respostas ("Atendimento Total", "Atendimento Parcial", "Não Atendida") são usadas para calcular a pontuação.
*   Geração de um dashboard com um gráfico de radar mostrando a pontuação final de cada categoria.

## Configuração e Execução

### Pré-requisitos

*   Python 3.x
*   `pip` (Python package installer)

### 1. Crie um Ambiente Virtual (Recomendado)

É uma boa prática usar um ambiente virtual para gerenciar as dependências do projeto.

```bash
python -m venv venv
```

Ative o ambiente virtual:

*   No Windows:
    ```bash
    .\venv\Scripts\activate
    ```
*   No macOS e Linux:
    ```bash
    source venv/bin/activate
    ```

### 2. Instale as Dependências

Com o ambiente virtual ativado, instale as dependências listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Execute a Aplicação Flask

Para iniciar o servidor de desenvolvimento Flask:

```bash
python app.py
```

A aplicação estará acessível em `http://127.0.0.1:5000` no seu navegador web.

## Estrutura do Projeto

*   `app.py`: Arquivo principal da aplicação Flask, contém as rotas e a lógica de negócio.
*   `requirements.txt`: Lista as dependências Python do projeto.
*   `templates/`: Contém os templates HTML (form.html, results.html).
*   `static/`: Contém os arquivos estáticos (style.css).
*   `README.md`: Este arquivo.

## Como Funciona

1.  Os dados do assessment (categorias, perguntas, pesos) estão atualmente hardcoded em `app.py` nas variáveis `ASSESSMENT_DATA` e `SCORING_MULTIPLIERS`.
2.  A rota `/` renderiza o `form.html`, que exibe as perguntas.
3.  Ao submeter o formulário, os dados são enviados para a rota `/submit` (via POST).
4.  A rota `/submit` calcula as pontuações para cada categoria com base nas respostas e pesos, e armazena os resultados na sessão do usuário.
5.  Em seguida, redireciona para a rota `/results`.
6.  A rota `/results` recupera as pontuações da sessão e as exibe no `results.html`, incluindo um gráfico de radar gerado com Chart.js.
