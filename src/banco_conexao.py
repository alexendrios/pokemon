import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


def obter_engine():
    """
    Cria e retorna um engine SQLAlchemy configurado para o banco de dados PostgreSQL.
    As variáveis de ambiente necessárias são:
        - POSTGRES_USERNAME: Nome de usuário do banco de dados
        - POSTGRES_PASSWORD: Senha do banco de dados
        - POSTGRES_HOST: Host do banco de dados
        - POSTGRES_PORT: Porta do banco de dados
        - POSTGRES_DB: Nome do banco de dados
        - REQUISITOS_SSL: Parâmetros SSL para a conexão (opcional)
    O parâmetro DB_PASSWORD é codificado para lidar com caracteres especiais.

    Retorna:
        sqlalchemy.engine.base.Engine: Engine SQLAlchemy para conexão com o banco

    Levanta:
        EnvironmentError: Caso alguma variável de ambiente obrigatória esteja ausente.
    """
    # Carrega variáveis de ambiente
    DB_USER = os.getenv("POSTGRES_USERNAME")
    DB_PASSWORD = quote_plus(
        os.getenv("POSTGRES_PASSWORD")
    )  # Codifica caracteres especiais
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_NAME = os.getenv("POSTGRES_DB")
    REQUISITOS_SSL = os.getenv("REQUISITOS_SSL")
    
    # Verifica se todas as variáveis estão presentes
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, REQUISITOS_SSL]):
        raise EnvironmentError(
            "❌ Variáveis de ambiente do banco estão incompletas. Verifique o arquivo .env"
        )

    # Constrói a URL de conexão
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}{REQUISITOS_SSL}"

    # Cria e retorna o engine SQLAlchemy
    engine = create_engine(DATABASE_URL)
    return engine
