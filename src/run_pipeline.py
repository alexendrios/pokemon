import os
import sys
import subprocess
import logging
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

from src.analisar_dados_banco import inicializar_dados
from src.report_analise import gerar_relatorio_pdf
from src.obtencao_dados import (
    verificar_saude,
    obter_token_jwt,
    obter_dados_pokemon,
    obter_atributos_pokemon,
    obter_dados_combate,
    transformar_csv,
)
from src.tratamento_dados import (
    informacoes_dataset,
    remover_duplicados,
    conectar_banco,
    gerar_pdf_report,
)

# ==================== Configuração de Logging ==================== #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
)

# ==================== Carrega .env ==================== #
load_dotenv()
OUT_DIR = os.getenv("OUT_DIR", "out")
REPORT_DIR = os.getenv("REPORT_DIR", "report")
DASHBOARD_PATH = os.getenv("DASHBOARD_PATH", "dashboard/dashboard.py")
USERNAME = os.getenv("API_USERNAME", "kaizen-poke")
PASSWORD = os.getenv("API_PASSWORD", "4w9f@D39fkkO")


def executar_pipeline(gerar_pdf=True, inserir_banco=True, iniciar_dashboard_flag=True):
    """Executa pipeline completo Pokémon Analytics"""
    logging.info("🏁 Iniciando pipeline Pokémon Analytics...")

    # -------------------- Autenticação -------------------- #
    logging.info("🔐 Obtendo token JWT...")
    response = obter_token_jwt()
    token = response.json().get("access_token") if response else None
    if not token:
        logging.error("❌ Falha ao obter token JWT. Encerrando pipeline.")
        return

    logging.info("✅ Token JWT obtido com sucesso!")
    verificar_saude(token)

    # -------------------- Coleta e transformação -------------------- #
    logging.info("📦 Coletando dados Pokémon...")
    lista_pokemon = obter_dados_pokemon(token)
    transformar_csv(lista_pokemon, "pokemons")

    logging.info("📊 Coletando atributos Pokémon...")
    lista_atributos = obter_atributos_pokemon(token)
    transformar_csv(lista_atributos, "atributos_pokemon")

    logging.info("⚔️ Coletando dados de combates...")
    lista_combates = obter_dados_combate(token)
    transformar_csv(lista_combates, "combates")

    # -------------------- Carregar CSVs -------------------- #
    try:
        df_pokemons = pd.read_csv(
            os.path.join(OUT_DIR, "pokemons.csv"), encoding="utf-8"
        )
        df_atributos = pd.read_csv(
            os.path.join(OUT_DIR, "atributos_pokemon.csv"), encoding="utf-8"
        )
        df_combates = pd.read_csv(
            os.path.join(OUT_DIR, "combates.csv"), encoding="utf-8"
        )
    except FileNotFoundError as e:
        logging.error(f"❌ Erro ao carregar CSVs: {e}")
        return

    # -------------------- Informações dos datasets -------------------- #
    logging.info(informacoes_dataset(df_pokemons, "pokemons"))
    logging.info(informacoes_dataset(df_atributos, "atributos_pokemon"))
    logging.info(informacoes_dataset(df_combates, "combates"))

    # -------------------- Limpeza -------------------- #
    df_combates = remover_duplicados(df_combates)

    # -------------------- Inserção no banco -------------------- #
    if inserir_banco:
        dfs = [df_pokemons, df_atributos, df_combates]
        tabelas = ["pokemons", "atributos_pokemon", "combates"]

        for df, tabela in zip(dfs, tabelas):
            try:
                conectar_banco(df, tabela)
            except Exception as e:
                logging.warning(f"⚠️ Erro ao inserir dados na tabela {tabela}: {e}")

    # -------------------- PDFs individuais -------------------- #
    if gerar_pdf:
        dfs = [df_pokemons, df_atributos, df_combates]
        tabelas = ["pokemons", "atributos_pokemon", "combates"]

        for df, tabela in zip(dfs, tabelas):
            try:
                gerar_pdf_report(
                    df, nome=tabela, pasta=os.path.join(REPORT_DIR, "tratamento")
                )
            except Exception as e:
                logging.warning(f"⚠️ Erro ao gerar PDF {tabela}: {e}")

    # -------------------- Relatório consolidado -------------------- #
    try:
        dados = inicializar_dados()
        if dados:
            logging.info("📄 Gerando relatório PDF final...")
            caminho = gerar_relatorio_pdf(
                dados, pasta=os.path.join(REPORT_DIR, "analises")
            )
            logging.info(f"✅ Relatório criado em: {caminho}")
        else:
            logging.warning("⚠️ Nenhum dado retornado por inicializar_dados().")
    except Exception as e:
        logging.exception(f"❌ Falha na geração do relatório final: {e}")

    logging.info("✅ Pipeline concluído com sucesso!")

    # -------------------- Dashboard Streamlit -------------------- #
    if iniciar_dashboard_flag:
        iniciar_dashboard()


def iniciar_dashboard():
    """Inicia o dashboard Streamlit"""
    logging.info("🚀 Iniciando dashboard Streamlit...")
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", DASHBOARD_PATH],
            check=True,
        )
    except FileNotFoundError:
        logging.error("❌ Streamlit não encontrado. Instale-o: pip install streamlit")
    except subprocess.CalledProcessError as e:
        logging.warning(f"⚠️ Erro ao iniciar dashboard Streamlit: {e}")
    except Exception as e:
        logging.exception(f"⚠️ Erro inesperado ao iniciar dashboard: {e}")


if __name__ == "__main__":
    executar_pipeline()
