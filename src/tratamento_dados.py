
import os
import io
import platform
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend não-gráfico (evita erro de Tcl/Tk)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from src.banco_conexao import obter_engine
import seaborn as sns

sns.set_style("whitegrid")


# ------------------ Funções de Apoio ------------------ #


def desenhar_linha(titulo=None):
    """
    Gera uma linha de separação visual para logs e relatórios.

    Args:
        titulo (str, optional): Título centralizado sobre a linha.

    Returns:
        str: Linha de 70 caracteres, opcionalmente com título.
    """
    linha = "=" * 70
    if titulo:
        return f"\n{linha}\n{titulo.center(70)}\n{linha}\n"
    return f"\n{linha}\n"


def resumo_qualidade(dataframe):
    """
    Gera resumo de qualidade dos dados, incluindo nulos e duplicados.

    Args:
        dataframe (pd.DataFrame): DataFrame a ser analisado.

    Returns:
        str: Resumo textual da qualidade dos dados.
    """
    return f"""{desenhar_linha("Qualidade dos Dados")}
Registros Nulos por Coluna:
{dataframe.isnull().sum()}
{desenhar_linha()}
Registros Duplicados: {dataframe.duplicated().sum()}
{desenhar_linha()}"""


def informacoes_dataset(dataframe: pd.DataFrame, nome: str) -> str:
    """
    Retorna informações detalhadas sobre o dataset, incluindo:
    - Info do DataFrame
    - Shape
    - Resumo categórico
    - Resumo numérico
    - Qualidade de dados (nulos e duplicados)

    Args:
        dataframe (pd.DataFrame): DataFrame a ser analisado.
        nome (str): Nome do dataset para identificação.

    Returns:
        str: Texto com o relatório completo do dataset.
    """
    nome = nome.lower().strip()
    buffer = io.StringIO()
    dataframe.info(buf=buffer)
    info_str = buffer.getvalue()

    saida = f"""
{info_str}
{desenhar_linha("Shape")}
{dataframe.shape}
"""

    # Resumo categórico
    cat_cols = dataframe.select_dtypes(include=["object", "category"])
    if not cat_cols.empty:
        saida += f"""{desenhar_linha("Resumo Categórico")}
{cat_cols.describe().transpose()}
"""
    else:
        saida += f"""{desenhar_linha("Resumo Categórico")}
Nenhuma coluna categórica encontrada.
"""

    # Resumo numérico
    num_cols = dataframe.select_dtypes(include=["number"])
    if not num_cols.empty:
        saida += f"""{desenhar_linha("Resumo Numérico")}
{num_cols.describe().transpose()}
"""
    else:
        saida += f"""{desenhar_linha("Resumo Numérico")}
Nenhuma coluna numérica encontrada.
"""

    saida += resumo_qualidade(dataframe)
    return saida


# ------------------ Transformações de Dados ------------------ #


def converter_tipos(df: pd.DataFrame, tipos: dict) -> pd.DataFrame:
    """
    Converte colunas de um DataFrame para tipos especificados.

    Args:
        df (pd.DataFrame): DataFrame a ser convertido.
        tipos (dict): Dicionário {coluna: tipo}.

    Returns:
        pd.DataFrame: DataFrame com colunas convertidas.
    """
    for coluna, tipo in tipos.items():
        if coluna in df.columns:
            try:
                df[coluna] = df[coluna].astype(tipo)
            except ValueError:
                df[coluna] = pd.to_numeric(df[coluna], errors="coerce").astype(tipo)
    return df


def remover_duplicados(df: pd.DataFrame, subset=None, keep="first") -> pd.DataFrame:
    """
    Remove registros duplicados de um DataFrame.

    Args:
        df (pd.DataFrame): DataFrame a ser limpo.
        subset (list, optional): Colunas para considerar duplicados.
        keep (str, optional): Qual registro manter ("first" ou "last").

    Returns:
        pd.DataFrame: DataFrame sem duplicados.
    """
    qtd_antes = len(df)
    df_sem_dup = df.drop_duplicates(subset=subset, keep=keep)
    qtd_depois = len(df_sem_dup)
    removidos = qtd_antes - qtd_depois

    print(desenhar_linha("Remoção de Duplicados"))
    if subset:
        print(f"Colunas consideradas: {subset}")
    print(f"Registros antes: {qtd_antes}")
    print(f"Registros depois: {qtd_depois}")
    print(f"Duplicados removidos: {removidos}")
    print(desenhar_linha())

    return df_sem_dup


# ------------------ Inserção em Banco de Dados ------------------ #


def inserir_dados(dataframe, engine, tabela):
    """
    Insere dados em uma tabela de banco via SQLAlchemy.

    Args:
        dataframe (pd.DataFrame): Dados a serem inseridos.
        engine (Engine): Engine SQLAlchemy.
        tabela (str): Nome da tabela no banco.
    """
    df = dataframe.copy()
    df["inserido_em"] = pd.Timestamp.utcnow()  # controle temporal
    df.to_sql(tabela, engine, if_exists="replace", index=False, method="multi")


def conectar_banco(dataframe, tabela, if_exists="replace"):
    """
    Conecta ao banco e insere dados.

    Args:
        dataframe (pd.DataFrame): Dados a serem inseridos.
        tabela (str): Nome da tabela.
        if_exists (str, optional): Comportamento se a tabela existir ("replace", "append").
    """
    engine = obter_engine()

    try:
        with engine.connect() as connection:
            print("✅ Conexão bem-sucedida")
            inserir_dados(dataframe, engine, tabela)
            print(f"✅ Dados inseridos na tabela {tabela}")
    except Exception as e:
        print("❌ Erro ao conectar ou inserir dados no banco")
        print(type(e).__name__, str(e))


# ------------------ Relatório PDF ------------------ #
def gerar_pdf_report(df: pd.DataFrame, nome: str = "Dataset", pasta: str = "report/tratamento"):
    """
    Gera um relatório PDF profissional com resumo, info(), shape, gráficos e estatísticas do DataFrame.
    """
    # === Metadados do relatório ===
    autor = os.getlogin()
    maquina = platform.node()
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Cria pasta se não existir
    os.makedirs(pasta, exist_ok=True)
    arquivo = os.path.join(pasta, f"{nome.lower().replace(' ', '_')}_report.pdf")

    # Função auxiliar para rodapé
    def adicionar_rodape(fig, pagina, total_paginas):
        rodape = f"Gerado por: {autor} ({maquina}) — {data_geracao} | Página {pagina}/{total_paginas}"
        fig.text(0.98, 0.02, rodape, ha="right", va="bottom", fontsize=8, color="gray")

    total_paginas = 6
    pagina = 1

    with PdfPages(arquivo) as pdf:
        # === Página 1: Capa estilizada ===
        fig, ax = plt.subplots(figsize=(8.27, 11.69))
        ax.axis("off")
        ax.text(0.5, 0.75, "📊 Relatório de Qualidade de Dados", ha="center", va="center", fontsize=28, fontweight="bold", color="#2E86C1")
        ax.text(0.5, 0.65, nome, ha="center", va="center", fontsize=22, fontweight="bold", color="#117A65")
        ax.text(0.5, 0.55, f"Gerado em: {data_geracao}", ha="center", va="center", fontsize=12, color="gray")
        adicionar_rodape(fig, pagina, total_paginas)
        pdf.savefig()
        plt.close()
        pagina += 1

        # === Página 2: Shape e Info ===
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_text = buffer.getvalue()
        fig, ax = plt.subplots(figsize=(8, 10))
        ax.axis("off")
        ax.text(0, 1, f"=== Estrutura do DataFrame ===\n\nShape: {df.shape}\n\n{info_text}",
                fontsize=9, family="monospace", verticalalignment="top")
        adicionar_rodape(fig, pagina, total_paginas)
        pdf.savefig()
        plt.close()
        pagina += 1

        # === Página 3: Resumo Geral com gráfico de nulos ===
        fig, ax = plt.subplots(figsize=(8, 6))
        nulos = df.isnull().sum()
        nulos = nulos[nulos > 0].sort_values()
        if not nulos.empty:
            sns.barplot(x=nulos.values, y=nulos.index, palette="Reds_r", ax=ax)
            ax.set_xlabel("Quantidade de Valores Nulos")
            ax.set_ylabel("Colunas")
            ax.set_title("Valores Nulos por Coluna", fontsize=14, fontweight="bold")
        else:
            ax.text(0.5, 0.5, "Nenhum valor nulo encontrado", ha="center", va="center", fontsize=12)
        adicionar_rodape(fig, pagina, total_paginas)
        pdf.savefig()
        plt.close()
        pagina += 1

        # === Página 4: Estatísticas Numéricas ===
        num_cols = df.select_dtypes(include=["number"])
        if not num_cols.empty:
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis("off")
            ax.text(0, 1, f"=== Estatísticas Numéricas ===\n\n{num_cols.describe().transpose()}",
                    verticalalignment="top", fontsize=9, family="monospace")
            adicionar_rodape(fig, pagina, total_paginas)
            pdf.savefig()
            plt.close()
            pagina += 1

        # === Página 5: Estatísticas Categóricas ===
        cat_cols = df.select_dtypes(include=["object", "category"])
        if not cat_cols.empty:
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis("off")
            ax.text(0, 1, f"=== Estatísticas Categóricas ===\n\n{cat_cols.describe().transpose()}",
                    verticalalignment="top", fontsize=9, family="monospace")
            adicionar_rodape(fig, pagina, total_paginas)
            pdf.savefig()
            plt.close()
            pagina += 1

        # === Página 6: Distribuição de algumas colunas numéricas (opcional) ===
        if not num_cols.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            num_cols.hist(ax=ax, bins=15, color="#3498DB", edgecolor="black")
            ax.set_title("Distribuição das Colunas Numéricas", fontsize=14, fontweight="bold")
            adicionar_rodape(fig, pagina, total_paginas)
            pdf.savefig()
            plt.close()

    print(f"✅ PDF gerado com sucesso: {arquivo}")
    return arquivo