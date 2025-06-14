import os
import streamlit as st
import pandas as pd  # Importamos o pandas para facilitar a exibição dos resultados
from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import NullPool
import sqlparse

# Importações do LangChain (não serão usadas no teste direto, mas permanecem para a função principal)
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
#from langchain_mistralai import ChatMistralAI

# --- Configuração da Página do Streamlit ---
st.set_page_config(page_title="Consulta DB com Agente SQL", layout="wide")
st.title("🤖 Consulta a Banco de Dados com Agente SQL e IA")
st.write("Faça perguntas em linguagem natural ou teste queries SQL diretamente.")

# --- Interface na Barra Lateral para Configurações ---
with st.sidebar:
    st.header("⚙️ Configurações")

    st.subheader("1. Banco de Dados")
    db_type = st.selectbox("Tipo de Banco", ["mysql", "postgresql"])
    db_host = st.text_input("Host", "localhost")
    db_port = st.text_input("Porta", "3306" if db_type == "mysql" else "5432")
    db_user = st.text_input("Usuário", "seu_usuario")
    db_password = st.text_input("Senha", type="password")
    db_name = st.text_input("Nome do Banco de Dados", "seu_banco_de_dados")

    connect_button = st.button("Conectar e Analisar Esquema")


# --- Funções do Backend ---
def get_db_engine(_db_type, _user, _password, _host, _port, _dbname):
    """Cria o 'engine' de conexão com o banco de dados usando SQLAlchemy."""
    if _db_type == 'mysql':
        connection_string = f"mysql+mysqlconnector://{_user}:{_password}@{_host}:{_port}/{_dbname}"
        engine = create_engine(connection_string, poolclass=NullPool)
    elif _db_type == 'postgresql':
        connection_string = f"postgresql+psycopg2://{_user}:{_password}@{_host}:{_port}/{_dbname}"
        engine = create_engine(connection_string)
    else:
        raise ValueError("Tipo de banco de dados não suportado.")
    return engine

# --- Lógica Principal da Aplicação ---
if connect_button:
    if not all([db_host, db_port, db_user, db_password, db_name]):
        st.warning("Por favor, preencha todas as credenciais do banco de dados.")
    else:
        try:
            with st.spinner("Conectando e carregando esquema do banco de dados..."):
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

if 'db_engine' in st.session_state:
    st.subheader("Esquema do Banco de Dados Conectado:")
    schema_display = st.session_state.get('schema_info', "")
    if schema_display:
        with st.expander("Clique para ver/ocultar o esquema", expanded=True):
            st.markdown(schema_display)
    else:
        st.info("O esquema do banco de dados está vazio ou não pôde ser carregado.")
    
    st.divider()
    # --- Seção de Teste Direto de SQL ---
    st.subheader("🧪 Teste Direto de Query SQL")
    st.write("Use esta seção para verificar sua conexão e executar comandos SQL manualmente.")
    
    manual_sql_query = st.text_area("Digite sua query SQL aqui:", height=100, key="manual_query")

    if st.button("Executar SQL Direto"):
        if not manual_sql_query:
            st.warning("Por favor, digite uma query SQL para testar.")
        else:
            try:
                with st.spinner("Executando query SQL..."):
                    engine = st.session_state['db_engine']
                    # Usamos o pandas para ler o resultado do SQL diretamente em um DataFrame
                                # Validação de Segurança e Execução

                st.subheader("Resultado da Consulta:")
                parsed_list = sqlparse.parse(manual_sql_query)
                
                if len(parsed_list) > 1 or (not parsed_list) or (parsed_list[0].get_type() != 'SELECT'):
                    st.error(f"❌ Ação Bloqueada! A IA gerou um comando que não é uma consulta de leitura (SELECT) única e segura.")
                else:
                    with st.spinner("🔄 Executando a consulta segura no banco de dados..."):
                        df = pd.read_sql(manual_sql_query, engine)
                        st.success("Query executada com sucesso!")
                        st.write("Resultado:")
                        st.dataframe(df)
            
            except Exception as e:
                st.error(f"Ocorreu um erro ao executar a query SQL: {e}")