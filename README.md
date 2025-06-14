# projeto-busca_text_to_sql
projeto de uma ferramente de busca em um banco de dados baseada em text-to-sql

## Dependências
Essa seção trata das dependências
### streamlit
Responsável pela interface interativa
### pandas
Para mostrar os resultados em um formato de tabelas
### sqlalchemy
Tem a função de comunicação com diferentes bancos de dados
### mysql-connector-python
Driver do sqlalchemy para conexão com MySQL
### psycopg2-binary
Driver do sqlalchemy para conexão com PostgreSQL
### langchain
Biblioteca responsável pelas ações com a IA, como:
- adaptação dos dados do sqlalchemy para compreensão do langchain
- utilização de templates para prompts e escrita de prompts personalizados
- tradução da linguagem natural para SQL
### langchain-google-genai
É conector específico para utilizarmos a API do Google Gemini como o cérebro da nossa aplicação.
### os
Cria a variável de ambiente para a chave de API no sistema operacional 
### re
Útil para tratar de expressões regulares. No código, é usado para tirar a marcação de bloco que a IA manda junto com a query (o `'''sql ..... '''`).
### Como instalar
Para instalar as dependências, basta rodar o seguinte comando no terminal:
    `pip install streamlit pandas sqlalchemy mysql-connector-python psycopg2-binary langchain langchain-google-genai sqlparse`

## Como rodar o código
Apenas utilize o seguinte comando: 
    `streamlit run nome_do_script.py`
