import pandas as pd
from sqlalchemy import text
from src.banco_conexao import obter_engine
import logging

logging.basicConfig(level=logging.INFO)


def conectar_banco():
    """Retorna SQLAlchemy engine."""
    return obter_engine()


def carregar_tabela(nome_tabela: str) -> pd.DataFrame:
    """Carrega tabela do banco. Retorna None em caso de falha."""
    engine = conectar_banco()
    try:
        df = pd.read_sql(text(f"SELECT * FROM {nome_tabela}"), engine)
        logging.info(f"Tabela '{nome_tabela}' carregada: {len(df)} linhas")
        return df
    except Exception as e:
        logging.warning(f"Não foi possível carregar '{nome_tabela}': {e}")
        return None


def salvar_tabela(df: pd.DataFrame, nome_tabela: str):
    """Salva DataFrame no banco (replace)."""
    engine = conectar_banco()
    try:
        df.to_sql(nome_tabela, engine, if_exists="replace", index=False, method="multi")
        logging.info(f"Tabela '{nome_tabela}' salva com {len(df)} linhas")
    except Exception as e:
        logging.error(f"Erro ao salvar tabela '{nome_tabela}': {e}")


# ------------------ Pipeline principal ------------------ #


def combinar_tabelas():
    """Combina combates com atributos, adicionando nomes e salvando 'combates_com_nomes'."""
    df_attr = carregar_tabela("atributos_pokemon")
    df_combates = carregar_tabela("combates")

    if df_attr is None or df_combates is None:
        logging.error(
            "Tabelas necessárias não encontradas (atributos_pokemon/combates)."
        )
        return None

    df_merged = (
        df_combates.merge(
            df_attr[["ID", "Nome"]], left_on="first_pokemon", right_on="ID", how="left"
        )
        .rename(columns={"Nome": "nome_first"})
        .drop(columns=["ID"])
        .merge(
            df_attr[["ID", "Nome"]], left_on="second_pokemon", right_on="ID", how="left"
        )
        .rename(columns={"Nome": "nome_second"})
        .drop(columns=["ID"])
        .merge(df_attr[["ID", "Nome"]], left_on="winner", right_on="ID", how="left")
        .rename(columns={"Nome": "nome_winner"})
        .drop(columns=["ID"])
    )

    salvar_tabela(df_merged, "combates_com_nomes")
    return df_merged


def gerar_estatisticas(df: pd.DataFrame):
    """Calcula vitórias, lutas, derrotas e taxa de vitória por Pokémon."""
    if df is None:
        logging.error("DataFrame de combates é None.")
        return None

    vitorias = df["nome_winner"].value_counts().reset_index()
    vitorias.columns = ["Pokemon", "Vitorias"]

    participacoes = (
        pd.concat([df["nome_first"], df["nome_second"]]).value_counts().reset_index()
    )
    participacoes.columns = ["Pokemon", "Lutas"]

    estatisticas = participacoes.merge(vitorias, on="Pokemon", how="left").fillna(0)
    estatisticas["Vitorias"] = estatisticas["Vitorias"].astype(int)
    estatisticas["Derrotas"] = estatisticas["Lutas"] - estatisticas["Vitorias"]
    estatisticas["Taxa_Vitoria(%)"] = (
        estatisticas.apply(
            lambda r: (r["Vitorias"] / r["Lutas"] * 100) if r["Lutas"] > 0 else 0,
            axis=1,
        )
    ).round(2)

    salvar_tabela(estatisticas, "estatisticas_pokemon")
    return estatisticas


def analisar_top10(df_estatisticas: pd.DataFrame):
    """Top 10 por vitórias e derrotas."""
    if df_estatisticas is None:
        return pd.DataFrame(), pd.DataFrame()

    top10_vitorias = df_estatisticas.nlargest(10, "Vitorias")
    top10_derrotas = df_estatisticas.nlargest(10, "Derrotas")

    salvar_tabela(top10_vitorias, "top10_vitorias")
    salvar_tabela(top10_derrotas, "top10_derrotas")
    return top10_vitorias, top10_derrotas


def analisar_top10_taxa_vitoria(df_estatisticas: pd.DataFrame, min_lutas: int = 5):
    """Top 10 por Taxa de Vitória (evita pokémons com poucas lutas)."""
    if df_estatisticas is None:
        return pd.DataFrame()

    df_filtrado = df_estatisticas[df_estatisticas["Lutas"] >= min_lutas]
    top10_taxa = df_filtrado.nlargest(10, "Taxa_Vitoria(%)")
    salvar_tabela(top10_taxa, "top10_taxa_vitoria")
    return top10_taxa


def analisar_atributos_top10(top10_vitorias: pd.DataFrame):
    """Compara atributos do top10 com a média geral."""
    df_attr = carregar_tabela("atributos_pokemon")
    if df_attr is None:
        logging.error("atributos_pokemon não encontrada.")
        return None, None, None

    df_top10_attr = df_attr[df_attr["Nome"].isin(top10_vitorias["Pokemon"])].copy()
    colunas_attr = df_attr.select_dtypes(include="number").columns

    medias_top10 = df_top10_attr[colunas_attr].mean().round(2)
    medias_geral = df_attr[colunas_attr].mean().round(2)

    comparativo = pd.DataFrame(
        {
            "Média_Top10": medias_top10,
            "Média_Geral": medias_geral,
            "Diferença": (medias_top10 - medias_geral).round(2),
        }
    ).sort_values(by="Diferença", ascending=False)

    salvar_tabela(df_top10_attr, "atributos_top10_vencedores")
    salvar_tabela(
        comparativo.reset_index().rename(columns={"index": "Atributo"}),
        "comparativo_atributos_top10",
    )
    return df_top10_attr, comparativo, df_attr


def analisar_correlacao(df_estatisticas: pd.DataFrame, df_attr: pd.DataFrame):
    """Calcula correlação entre atributos numéricos e número de vitórias."""
    if df_estatisticas is None or df_attr is None:
        return pd.DataFrame()

    df_merge = df_estatisticas.merge(
        df_attr, left_on="Pokemon", right_on="Nome", how="left"
    )
    colunas_num = df_attr.select_dtypes(include="number").columns.tolist()
    if "Vitorias" not in df_merge.columns:
        return pd.DataFrame()

    cols = [c for c in colunas_num + ["Vitorias"] if c in df_merge.columns]
    corr = df_merge[cols].corr()["Vitorias"].drop("Vitorias").reset_index()
    corr.columns = ["Atributo", "Correlação_com_Vitórias"]
    corr = corr.sort_values("Correlação_com_Vitórias", ascending=False)

    salvar_tabela(corr, "correlacao_atributos_vitorias")
    return corr


def analisar_distribuicao_taxa(df_estatisticas: pd.DataFrame):
    """Gera distribuição por faixas da Taxa_Vitoria(%)"""
    if df_estatisticas is None:
        return pd.DataFrame()

    bins = [0, 25, 50, 75, 100]
    labels = ["0-25%", "25-50%", "50-75%", "75-100%"]
    df_estatisticas["Faixa_Taxa_Vitoria"] = pd.cut(
        df_estatisticas["Taxa_Vitoria(%)"].fillna(0),
        bins=bins,
        labels=labels,
        include_lowest=True,
    )
    dist = (
        df_estatisticas["Faixa_Taxa_Vitoria"]
        .value_counts(normalize=True)
        .reindex(labels)
        .fillna(0)
        .reset_index()
    )
    dist.columns = ["Faixa", "Proporção"]
    dist["Proporção(%)"] = (dist["Proporção"] * 100).round(2)

    salvar_tabela(dist, "distribuicao_taxa_vitoria")
    return dist


def analisar_tipo(df_estatisticas, df_atributos):
    """
    Analisa o desempenho dos tipos de Pokémon com base na taxa média de vitória.
    Cria a tabela 'ranking_tipos_vitoria'.
    Compatível com coluna 'Types' do atributos_pokemon.
    """
    try:
        if "Types" not in df_atributos.columns:
            logging.warning("Coluna 'Types' não encontrada no DataFrame de atributos.")
            return None

        # Junta estatísticas com tipos
        df_merged = df_estatisticas.merge(
            df_atributos[["Nome", "Types"]],
            left_on="Pokemon",
            right_on="Nome",
            how="left",
        )

        # Calcula taxa de vitória
        df_merged["taxa_vitoria"] = df_merged["Vitorias"] / df_merged["Lutas"]
        df_merged["taxa_vitoria"] = df_merged["taxa_vitoria"].fillna(0)

        # Agrupa por tipo e calcula média
        df_tipo = (
            df_merged.groupby("Types")
            .agg(
                media_taxa_vitoria=("taxa_vitoria", "mean"),
                total_vitorias=("Vitorias", "sum"),
                total_batalhas=("Lutas", "sum"),
            )
            .reset_index()
            .sort_values("media_taxa_vitoria", ascending=False)
        )

        # Adiciona ranking
        df_tipo["ranking"] = range(1, len(df_tipo) + 1)

        # Salva tabela
        salvar_tabela(df_tipo, "ranking_tipos_vitoria")
        logging.info(f"Tabela 'ranking_tipos_vitoria' salva com {len(df_tipo)} linhas")

        return df_tipo

    except Exception as e:
        logging.warning(f"Erro ao gerar ranking de tipos: {e}")
        return None

# ------------------ Ajuste final de limpeza ------------------ #

def inicializar_dados():
    """Carrega tabelas analíticas existentes ou gera se necessário."""
    # Carregar tudo o que existir
    top10_vitorias = carregar_tabela("top10_vitorias")
    top10_derrotas = carregar_tabela("top10_derrotas")
    top10_taxa = carregar_tabela("top10_taxa_vitoria")
    correlacoes = carregar_tabela("correlacao_atributos_vitorias")
    distribuicao = carregar_tabela("distribuicao_taxa_vitoria")
    ranking_tipos = carregar_tabela("ranking_tipos_vitoria")
    comparativo = carregar_tabela("comparativo_atributos_top10")
    df_top10_attr = carregar_tabela("atributos_top10_vencedores")
    df_attr_geral = carregar_tabela("atributos_pokemon")

    if df_attr_geral is None:
        logging.info("Base de atributos não encontrada. Abortando.")
        return None

    df_completo = carregar_tabela("combates_com_nomes")
    if df_completo is None:
        df_completo = combinar_tabelas()

    df_estatisticas = carregar_tabela("estatisticas_pokemon")
    if df_estatisticas is None and df_completo is not None:
        df_estatisticas = gerar_estatisticas(df_completo)

    if top10_vitorias is None or top10_derrotas is None:
        top10_vitorias, top10_derrotas = analisar_top10(df_estatisticas)

    if top10_taxa is None:
        top10_taxa = analisar_top10_taxa_vitoria(df_estatisticas)

    if df_top10_attr is None or comparativo is None:
        df_top10_attr, comparativo, df_attr_geral = analisar_atributos_top10(
            top10_vitorias
        )

    if correlacoes is None:
        correlacoes = analisar_correlacao(df_estatisticas, df_attr_geral)

    if distribuicao is None:
        distribuicao = analisar_distribuicao_taxa(df_estatisticas)

    if ranking_tipos is None:
        ranking_tipos = analisar_tipo(df_estatisticas, df_attr_geral)

    return (
        top10_vitorias,
        top10_derrotas,
        top10_taxa,
        correlacoes,
        distribuicao,
        ranking_tipos,
        df_top10_attr,
        comparativo,
        df_attr_geral,
    )
