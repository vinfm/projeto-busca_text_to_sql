import os
import streamlit as st
from sqlalchemy import create_engine, inspect
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_mistralai import ChatMistralAI

# ... (todo o código inicial permanece o mesmo) ...

st.set_page_config(page_title="Consulta DB com Linguagem Natural", layout="wide")
st.title("🤖 Consulta a Banco de Dados com Agente SQL")
st.sidebar.header("Configuração do Banco de Dados")
db_type = st.sidebar.selectbox("Tipo de Banco", ["postgresql", "mysql"])
db_host = st.sidebar.text_input("Host", "localhost")
db_port = st.sidebar.text_input("Porta", "5432" if db_type == "postgresql" else "3306")
db_user = st.sidebar.text_input("Usuário", "seu_usuario")
db_password = st.sidebar.text_input("Senha", type="password")
db_name = st.sidebar.text_input("Nome do Banco de Dados", "seu_banco_de_dados")
st.sidebar.header("Configuração da Mistral AI")
mistral_api_key = st.sidebar.text_input("Sua Chave de API da Mistral", type="password")


@st.cache_resource(ttl=3600)
def get_db_engine(_db_type, _user, _password, _host, _port, _dbname):
    if _db_type == 'mysql':
        connection_string = f"mysql+mysqlconnector://{_user}:{_password}@{_host}:{_port}/{_dbname}"
    elif _db_type == 'postgresql':
        connection_string = f"postgresql+psycopg2://{_user}:{_password}@{_host}:{_port}/{_dbname}"
    else:
        raise ValueError("Tipo de banco de dados não suportado.")
    engine = create_engine(connection_string)
    return engine

# Corpo Principal da Aplicação

if st.sidebar.button("Conectar e Analisar Esquema"):
    if not all([db_host, db_port, db_user, db_password, db_name]):
        st.warning("Por favor, preencha todas as credenciais do banco de dados.")
    else:
        try:
            engine = get_db_engine(db_type, db_user, db_password, db_host, db_port, db_name)
            st.session_state['db_engine'] = engine
            st.success(f"Conexão com {db_type} estabelecida com sucesso!")
            
            inspector = inspect(engine)
            schemas = inspector.get_schema_names()
            
            with st.expander("Ver Esquema do Banco de Dados"):
                for schema in schemas:
                     if not schema.startswith('pg_') and schema != 'information_schema':
                        st.write(f"**Esquema:** `{schema}`")
                        for table_name in inspector.get_table_names(schema=schema):
                            st.write(f"  - **Tabela:** `{table_name}`")
                            columns = inspector.get_columns(table_name, schema=schema)
                            for column in columns:
                                st.write(f"    - Campo: `{column['name']}` (Tipo: `{column['type']}`)")
        except Exception as e:
            st.error(f"Erro ao conectar ou analisar o banco de dados: {e}")

if 'db_engine' in st.session_state:
    st.header("Faça sua pergunta")
    natural_language_query = st.text_area("Digite sua pergunta em linguagem natural aqui:")
    if st.button("Executar Consulta"):
        if not mistral_api_key:
            st.warning("Por favor, insira sua chave da API da Mistral na barra lateral.")
        elif not natural_language_query:
            st.warning("Por favor, digite uma pergunta.")
        else:
            try:
                os.environ["MISTRAL_API_KEY"] = mistral_api_key
                engine = st.session_state['db_engine']
                db = SQLDatabase(engine=engine)
                llm = ChatMistralAI(model="mistral-large-latest", temperature=0)

                # --- MUDANÇA APLICADA AQUI ---
                # Removemos o parâmetro agent_type="openai-tools" para usar
                # um agente mais genérico e compatível com a Mistral.
                agent_executor = create_sql_agent(llm, db=db, verbose=True)

                with st.spinner("Agente SQL pensando e executando a consulta..."):
                    response = agent_executor.invoke({"input": natural_language_query})
                    result = response.get("output", "Não foi possível obter uma resposta.")

                st.subheader("Resultado da Consulta")
                st.markdown(result)
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar sua consulta: {e}")