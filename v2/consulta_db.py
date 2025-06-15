import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import NullPool
import sqlparse
import re

# Importações do LangChain
from langchain_core.prompts import ChatPromptTemplate
from langchain.sql_database import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain

# --- Configuração da Página do Streamlit ---
st.set_page_config(page_title="Natural Language to SQL", layout="wide")
st.title("🗣️ Linguagem Natural para SQL (Interface Segura e Dinâmica)")
st.write("Forneça as configurações, conecte-se ao banco, e faça perguntas para gerar e executar consultas SQL.")

# --- Interface na Barra Lateral para Configurações ---
with st.sidebar:
    st.header("⚙️ Configurações da Sessão")
    st.subheader("1. Banco de Dados")
    db_type = st.selectbox("Tipo de Banco", ["mysql", "postgresql"])
    db_host = st.text_input("Host", "localhost")
    db_port = st.text_input("Porta", "3306" if db_type == "mysql" else "5432")
    db_user = st.text_input("Usuário", placeholder="ex: seu_usuario")
    db_password = st.text_input("Senha", type="password")
    db_name = st.text_input("Nome do Banco de Dados", placeholder="ex: meu_banco")
    st.subheader("2. Inteligência Artificial")
    google_api_key = st.text_input("Sua Chave de API do Google AI", type="password")
    connect_button = st.button("Conectar e Analisar Esquema")


# --- Funções do Backend ---
def get_db_engine(_db_type, _user, _password, _host, _port, _dbname):
    """Cria o 'engine' de conexão com o banco de dados."""
    if _db_type == 'mysql':
        connection_string = f"mysql+mysqlconnector://{_user}:{_password}@{_host}:{_port}/{_dbname}"
        engine = create_engine(connection_string, poolclass=NullPool)
    elif _db_type == 'postgresql':
        connection_string = f"postgresql+psycopg2://{_user}:{_password}@{_host}:{_port}/{_dbname}"
        engine = create_engine(connection_string)
    else:
        raise ValueError("Tipo de banco de dados não suportado.")
    return engine

# --- Lógica de Conexão e Análise de Esquema ---
if connect_button:
    if 'schema_info' in st.session_state:
        del st.session_state['schema_info']
    if 'db_engine' in st.session_state:
        del st.session_state['db_engine']
    
    if not all([db_host, db_port, db_user, db_password, db_name]):
        st.warning("Por favor, preencha todas as credenciais do banco de dados na barra lateral.")
    else:
        try:
            with st.spinner("Conectando ao banco de dados e analisando o esquema..."):
                engine = get_db_engine(db_type, db_user, db_password, db_host, db_port, db_name)
                st.session_state['db_engine'] = engine

                inspector = inspect(engine)
                
                schema_info_string = f"**Analisando o banco de dados/esquema:** `{db_name}`\n"
                
                table_names = inspector.get_table_names()

                if not table_names:
                     st.warning(f"Nenhuma tabela encontrada no banco de dados '{db_name}'. Verifique as permissões do usuário ou se o banco contém tabelas.")
                
                for table_name in table_names:
                    schema_info_string += f"  - **Tabela:** `{table_name}`\n"
                    columns = inspector.get_columns(table_name)
                    for column in columns:
                        schema_info_string += f"    - Campo: `{column['name']}` (Tipo: `{column['type']}`)\n"
                
                st.session_state['schema_info'] = schema_info_string

            st.success(f"Conexão com {db_type} estabelecida com sucesso!")
            
        except Exception as e:
            st.error(f"Ocorreu um erro detalhado ao conectar ou analisar o banco de dados: {e}")

# --- Lógica Principal da Interface --
if 'db_engine' in st.session_state:
    st.subheader("Esquema do Banco de Dados Conectado:")
    schema_display = st.session_state.get('schema_info', "")
    if schema_display:
        with st.expander("Clique para ver/ocultar o esquema", expanded=True):
            st.markdown(schema_display)
    else:
        st.info("O esquema do banco de dados está vazio ou não pôde ser carregado.")
    
    st.divider()

    st.subheader("Faça sua pergunta")
    natural_language_query = st.text_area("Digite sua consulta em linguagem natural aqui:", height=100, key="ia_query")

    if st.button("Gerar e Executar SQL"):

        if 'generated_sql' in st.session_state:
            del st.session_state.generated_sql
        if 'result_df' in st.session_state:
            del st.session_state.result_df
        
        if not google_api_key:
            st.warning("Por favor, insira sua chave da API do Google AI.")
        elif not natural_language_query:
            st.warning("Por favor, digite uma pergunta.")
        else:
            try:
                os.environ["GOOGLE_API_KEY"] = google_api_key
                engine = st.session_state['db_engine']
                db = SQLDatabase(engine=engine)
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)

                prompt = ChatPromptTemplate.from_template(
                    """Sua única tarefa é receber uma pergunta e o esquema de um banco de dados e gerar uma única e sintaticamente correta consulta SQL de leitura (SELECT).
                    Dialeto SQL a ser usado: {dialect}.
                    
                    Regras Importantes:
                    - NUNCA gere comandos DML (INSERT, UPDATE, DELETE) ou DDL (CREATE, ALTER, DROP). **SE** a pergunta do usuário pedir para modificar o banco de dados (usando palavras como CRIAR, INSERIR, ALTERAR, APAGAR, ATUALIZAR, DROP, INSERT, UPDATE, DELETE, CREATE, ALTER), você **NÃO DEVE** gerar SQL. Em vez disso, sua resposta final e direta para o usuário deve ser uma frase educada em português explicando que você não tem permissão para realizar esse tipo de operação, como por exemplo: "Desculpe, minhas permissões são apenas para leitura e não posso alterar o banco de dados."
                    - A menos que o usuário peça um número específico de resultados, você pode usar o valor sugerido de {top_k} para limitar os resultados. Se o usuário pedir "todos", não adicione um LIMIT.
                    - Atente-se aos alias de tabelas e colunas que podem ser usados pelo usuário, se necessário.
                    - Sempre use nomes de colunas e tabelas exatamente como estão no esquema.
                    - Sua saída deve ser APENAS o código SQL puro, sem nenhuma formatação Markdown como ```sql, explicações ou qualquer outro texto.

                    Esquema do banco:
                    {table_info}
                    
                    Pergunta do usuário:
                    {input}
                    
                    SQL Query:"""

                )
                
                with st.spinner("🤖 IA está traduzindo sua pergunta para SQL..."):
                    # A cadeia agora recebe um prompt com as variáveis corretas.
                    query_chain = create_sql_query_chain(llm, db, prompt=prompt)
                    generated_sql = query_chain.invoke({"question": natural_language_query}).strip()

                    # Limpeza da saída da IA para remover formatação Markdown
                    match = re.search(r"```sql\n(.*)\n```", generated_sql, re.DOTALL)
                    if match:
                        generated_sql = match.group(1).strip()
                    else:
                        generated_sql = generated_sql.strip('`').strip()

                st.session_state.generated_sql = generated_sql

                # Validação e Execução
                parsed_list = sqlparse.parse(generated_sql)
                non_empty_statements = [stmt for stmt in parsed_list if stmt.tokens and str(stmt).strip()]

                if len(non_empty_statements) != 1 or non_empty_statements[0].get_type() != 'SELECT':
                    st.error(f"❌ Ação Bloqueada! A IA gerou um comando inválido.")
                    # Limpa o SQL inválido do estado
                    del st.session_state.generated_sql 
                else:
                    with st.spinner("🔄 Executando a consulta segura no banco de dados..."):
                        df = pd.read_sql(generated_sql, engine)

                        st.session_state.result_df = df

            except Exception as e:
                st.error(f"Ocorreu um erro durante o processo: {e}")

    if 'generated_sql' in st.session_state:
        st.subheader("Query SQL Gerada:")
        st.code(st.session_state.generated_sql, language='sql')

    if 'result_df' in st.session_state:
        st.subheader("Resultado da Consulta:")
        st.dataframe(st.session_state.result_df)