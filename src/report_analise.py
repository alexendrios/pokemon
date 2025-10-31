import matplotlib
matplotlib.use("Agg")  # <-- backend sem dependência de Tcl/Tk
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
from datetime import datetime
import logging
import os
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd

logging.basicConfig(level=logging.INFO)


def _df_safe(df):
    """Garante um DataFrame não nulo para uso em tabelas."""
    if df is None:
        return pd.DataFrame()
    return df


def _table_from_df(df: pd.DataFrame, max_rows: int = 20):
    """
    Converte DataFrame em lista de listas para reportlab Table.
    Limita a max_rows (inclui cabeçalho).
    """
    df = _df_safe(df)
    if df.empty:
        return [["(vazio)"]]
    rows = [df.columns.tolist()] + df.head(max_rows - 1).values.tolist()
    # Converte numpy types para tipos nativos (para evitar problemas)
    cleaned = []
    for r in rows:
        cleaned.append(
            [
                str(x)
                if (isinstance(x, (float, int)) and pd.isna(x)) or x is None
                else x
                for x in r
            ]
        )
    return cleaned


def _matplotlib_to_reportlab_image(fig, width=450, height=300):
    """Converte figura Matplotlib para reportlab.platypus.Image via BytesIO."""
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img = Image(buf, width=width, height=height)
    plt.close(fig)
    return img


def gerar_relatorio_pdf(
    dados_pipeline,
    nome_arquivo="report_pipeline_pokemon.pdf",
    pasta="report/analises",
):
    """
    Gera um relatório em PDF com o resumo do pipeline, tabelas e gráficos.
    Espera que dados_pipeline seja a tupla retornada por inicializar_dados().
    """
    if not os.path.exists(pasta):
        os.makedirs(pasta, exist_ok=True)

    caminho_pdf = os.path.join(pasta, nome_arquivo)

    (
        top10_vitorias,
        top10_derrotas,
        top10_taxa,
        correlacoes,
        distribuicao,
        ranking_tipos,
        df_top10_attr,
        comparativo,
        df_attr_geral,
    ) = dados_pipeline

    # normaliza para evitar None
    top10_vitorias = _df_safe(top10_vitorias)
    top10_derrotas = _df_safe(top10_derrotas)
    top10_taxa = _df_safe(top10_taxa)
    correlacoes = _df_safe(correlacoes)
    distribuicao = _df_safe(distribuicao)
    ranking_tipos = _df_safe(ranking_tipos)
    df_top10_attr = _df_safe(df_top10_attr)
    comparativo = _df_safe(comparativo)
    df_attr_geral = _df_safe(df_attr_geral)
    
    for df in [correlacoes, comparativo, df_attr_geral]:
        if "ID" in df.columns:
            df.drop(columns=["ID"], inplace=True)

    correlacoes = correlacoes[correlacoes["Atributo"] != "ID"]
    comparativo = comparativo[comparativo["Atributo"] != "ID"]

    doc = SimpleDocTemplate(caminho_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # --- Capa ---
    story.append(
        Paragraph(
            "<b>Pipeline de Extração, Transformação e Análises - Dashboard Pokémon</b>",
            styles["Title"],
        )
    )
    story.append(Spacer(1, 20))
    story.append(Paragraph("Autor: <b>Alexandre Pereira Santos</b>", styles["Normal"]))
    story.append(
        Paragraph(
            f"Data de execução: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "Relatório gerado automaticamente pelo pipeline de dados Pokémon. Contém tabelas analíticas e gráficos "
            "destinados ao consumo pelo dashboard Streamlit.",
            styles["BodyText"],
        )
    )
    story.append(PageBreak())

    # --- Sumário Executivo ---
    story.append(Paragraph("<b>Sumário Executivo</b>", styles["Heading1"]))
    story.append(
        Paragraph(
            "Este relatório apresenta as etapas de extração, transformação e análise dos dados de combates Pokémon, "
            "com geração de tabelas analíticas para consumo em um dashboard interativo via Streamlit.",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 12))

    tabelas_geradas = [
        ["Tabela", "Registros"],
        ["top10_vitorias", len(top10_vitorias)],
        ["top10_derrotas", len(top10_derrotas)],
        ["top10_taxa_vitoria", len(top10_taxa)],
        ["ranking_tipos_vitoria", len(ranking_tipos)],
        ["comparativo_atributos_top10", len(comparativo)],
        ["correlacao_atributos_vitorias", len(correlacoes)],
        ["distribuicao_taxa_vitoria", len(distribuicao)],
    ]

    tabela_sumario = Table(tabelas_geradas, hAlign="LEFT")
    tabela_sumario.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(tabela_sumario)
    story.append(PageBreak())

    # --- Resultados Analíticos (Tabelas) ---
    story.append(
        Paragraph("<b>Top 10 Pokémon com Mais Vitórias</b>", styles["Heading2"])
    )
    story.append(Table(_table_from_df(top10_vitorias, max_rows=12)))
    story.append(Spacer(1, 12))

    story.append(
        Paragraph("<b>Top 10 Pokémon com Mais Derrotas</b>", styles["Heading2"])
    )
    story.append(Table(_table_from_df(top10_derrotas, max_rows=12)))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Top 10 por Taxa de Vitória</b>", styles["Heading2"]))
    story.append(Table(_table_from_df(top10_taxa, max_rows=12)))
    story.append(PageBreak())

    story.append(
        Paragraph(
            "<b>Ranking de Tipos por Taxa Média de Vitória</b>", styles["Heading2"]
        )
    )
    story.append(Table(_table_from_df(ranking_tipos, max_rows=12)))
    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "<b>Correlação entre Atributos e Número de Vitórias</b>", styles["Heading2"]
        )
    )
    story.append(Table(_table_from_df(correlacoes, max_rows=12)))
    story.append(Spacer(1, 12))

    story.append(
        Paragraph("<b>Distribuição da Taxa de Vitória</b>", styles["Heading2"])
    )
    story.append(Table(_table_from_df(distribuicao, max_rows=12)))
    story.append(PageBreak())

    # --- Gráficos (Matplotlib embutido) ---
    # Função auxiliar local para adicionar figura ao story
    def _add_fig_to_story(fig, w=450, h=300):
        img = _matplotlib_to_reportlab_image(fig, width=w, height=h)
        story.append(img)
        story.append(Spacer(1, 12))

    # Top 10 Vitórias - gráfico horizontal
    if not top10_vitorias.empty:
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            # selecionar até 10
            top = top10_vitorias.head(10).sort_values("Vitorias", ascending=True)
            ax.barh(top["Pokemon"].astype(str), top["Vitorias"].astype(float))
            ax.set_xlabel("Vitórias")
            ax.set_title("Top 10 Pokémon por Vitórias")
            _add_fig_to_story(fig)
        except Exception as e:
            logging.warning(f"Erro ao gerar gráfico Top10 Vitórias: {e}")

    # Ranking tipos - barras
    if not ranking_tipos.empty:
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            top_types = ranking_tipos.head(15)
            ax.bar(
                top_types["Types"].astype(str),
                top_types["media_taxa_vitoria"].astype(float),
            )
            ax.set_xlabel("Tipo")
            ax.set_ylabel("Taxa Média de Vitória")
            ax.set_title("Ranking de Tipos - Taxa Média de Vitória")
            plt.xticks(rotation=45, ha="right")
            _add_fig_to_story(fig)
        except Exception as e:
            logging.warning(f"Erro ao gerar gráfico Ranking Tipos: {e}")

    # Correlações - horizontal
    if not correlacoes.empty:
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            corr_plot = correlacoes.head(10).sort_values(
                "Correlação_com_Vitórias", ascending=True
            )
            ax.barh(
                corr_plot["Atributo"].astype(str),
                corr_plot["Correlação_com_Vitórias"].astype(float),
            )
            ax.set_xlabel("Correlação com Vitórias")
            ax.set_title("Correlação entre Atributos e Vitórias (Top 10)")
            _add_fig_to_story(fig)
        except Exception as e:
            logging.warning(f"Erro ao gerar gráfico Correlações: {e}")

    # Distribuição - pizza / barras (se tiver proporção)
    if not distribuicao.empty and "Proporção(%)" in distribuicao.columns:
        try:
            fig, ax = plt.subplots(figsize=(6, 4))
            labels = distribuicao["Faixa"].astype(str).tolist()
            sizes = distribuicao["Proporção(%)"].astype(float).tolist()
            # fallback para barras se só um item
            if len(sizes) > 1:
                ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
                ax.set_title("Distribuição por Faixa de Taxa de Vitória (%)")
            else:
                ax.bar(labels, sizes)
                ax.set_title("Distribuição por Faixa de Taxa de Vitória (%)")
            _add_fig_to_story(fig, w=350, h=250)
        except Exception as e:
            logging.warning(f"Erro ao gerar gráfico Distribuição: {e}")

    # Comparativo atributos - barras (diferença)
    if not comparativo.empty and "Diferença" in comparativo.columns:
        try:
            top_attrs = comparativo.sort_values("Diferença", ascending=False).head(10)
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.barh(
                top_attrs["Atributo"].astype(str), top_attrs["Diferença"].astype(float)
            )
            ax.set_xlabel("Diferença (Top10 - Média Geral)")
            ax.set_title("Atributos com maior diferença (Top10 vs Média Geral)")
            ax.invert_yaxis()
            _add_fig_to_story(fig)
        except Exception as e:
            logging.warning(f"Erro ao gerar gráfico Comparativo Atributos: {e}")

    story.append(PageBreak())

    # --- Comparativo Atributos Tabela (detalhe) ---
    story.append(
        Paragraph(
            "<b>Comparativo de Atributos - Top 10 vs Média Geral</b>",
            styles["Heading1"],
        )
    )
    story.append(Table(_table_from_df(comparativo, max_rows=20)))

    story.append(PageBreak())

    # --- Conclusões ---
    story.append(Paragraph("<b>Conclusões</b>", styles["Heading1"]))
    story.append(
        Paragraph(
            "As análises demonstram quais Pokémon apresentam maior desempenho em batalhas, bem como a influência dos "
            "atributos em vitórias. O resultado é usado para alimentar dashboards analíticos e apoiar futuras decisões "
            "sobre balanceamento e estatísticas comparativas.",
            styles["Normal"],
        )
    )

    # build PDF
    try:
        doc.build(story)
        logging.info(f"✅ Relatório PDF gerado com sucesso: {caminho_pdf}")
    except Exception as e:
        logging.error(f"Erro ao construir o PDF: {e}")
        raise

    return caminho_pdf