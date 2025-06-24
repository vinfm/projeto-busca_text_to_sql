# 🔍 Projeto Busca Text-to-SQL com IA Generativa

Este projeto apresenta uma ferramenta poderosa e intuitiva que traduz linguagem natural em consultas SQL. Utilizando a API do Google Gemini, a aplicação permite que usuários interajam com bancos de dados e extraiam informações sem precisar escrever uma única linha de código SQL.

A interface, construída com Streamlit, oferece uma experiência de usuário simples e direta: você se conecta ao banco de dados, faz uma pergunta, e a ferramenta gera a consulta SQL correspondente, exibindo os resultados em uma tabela.

---

## ✨ Funcionalidades Principais

* **Tradução de Linguagem Natural para SQL:** Pergunte em português "Quais clientes fizeram mais de 3 pedidos no último mês?" e obtenha o código SQL e os resultados.
* **Interface Web Interativa:** Interface limpa e fácil de usar desenvolvida com Streamlit.
* **Suporte a Múltiplos Bancos de Dados:** Conecte-se facilmente a bancos de dados **MySQL** e **PostgreSQL**.
* **Visualização de Resultados:** Os dados retornados pela consulta são exibidos de forma clara em tabelas usando Pandas.
* **Transparência:** O código SQL gerado pela IA é exibido, permitindo auditoria e aprendizado.

---

## ⚙️ Como Funciona

O projeto utiliza um fluxo de trabalho inteligente para converter texto em SQL:

1.  **Conexão e Schema:** A ferramenta se conecta ao banco de dados selecionado usando **SQLAlchemy** e lê o schema (estrutura das tabelas e colunas).
2.  **Orquestração com LangChain:** O **LangChain** atua como o cérebro da operação. Ele pega o schema do banco e a pergunta do usuário.
3.  **Prompt Engineering:** As informações são inseridas em um *prompt* otimizado, que instrui o modelo de linguagem (Google Gemini) a se comportar como um especialista em SQL e traduzir a pergunta do usuário para uma consulta válida para o dialeto SQL específico (MySQL, PostgreSQL, etc.).
4.  **Geração da Query:** A API **Google Gemini** processa o prompt e gera a consulta SQL.
5.  **Limpeza e Execução:** A consulta é limpa de formatações desnecessárias (como a marcação de bloco de código) e executada no banco de dados.
6.  **Exibição dos Dados:** O resultado é formatado em um DataFrame do **Pandas** e exibido na interface do **Streamlit**.

---

## 🛠️ Dependências e Tecnologias

Esta seção detalha as bibliotecas que dão vida ao projeto.

### Interface e Exibição de Dados
* **streamlit:** Responsável pela criação da interface web interativa.
* **pandas:** Utilizado para exibir os resultados das consultas em formato de tabelas (DataFrames).

### Conectividade com Banco de Dados
* **sqlalchemy:** Atua como uma camada de abstração (ORM) para comunicação com diferentes bancos de dados SQL.
* **mysql-connector-python:** Driver específico para a conexão com bancos de dados **MySQL**.
* **psycopg2-binary:** Driver específico para a conexão com bancos de dados **PostgreSQL**.

### Inteligência Artificial e Orquestração
* **langchain:** A principal biblioteca para orquestrar as interações com a IA. Ela gerencia o schema, formata os prompts e processa a tradução para SQL.
* **langchain-google-genai:** Conector que integra o LangChain com a API do Google Gemini, o cérebro da nossa aplicação.

### Utilitários
* **os:** Usado para gerenciar variáveis de ambiente, como a chave da API do Google.
* **re:** Biblioteca de expressões regulares, utilizada aqui para limpar a formatação da query SQL gerada pela IA (remove o markdown `'''sql ... '''`).

### Instalação
Para o código, foi utilizado a versão 3.11 do Python. A seguir temos os passos para instalar as dependências do projeto.

Para criar o ambiente virtual, ativá-lo e  instalar todas as dependências de uma vez, abra seu terminal no diretório "scripts" e execute o seguinte comando:

```bash
### Criação do ambiente virtual
python -m venv venv 

### Ativação venv em Linux
source venv/bin/activate

### Instalação das dependências 
pip install -r requirements.txt

### Executar a aplicação Streamlit
```bash
streamlit run consulta_db.py
