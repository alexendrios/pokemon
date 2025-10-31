import streamlit as st
import pandas as pd
import plotly.express as px
from src.analisar_dados_banco import inicializar_dados, carregar_tabela

st.set_page_config(page_title="Pokémon Analyst Dashboard", layout="wide")
st.title("Pokémon Analyst Dashboard ⚡")


# ------------------ Funções utilitárias ------------------ #
def clean_df(df):
    """Remove ID e reseta o índice para evitar colunas indesejadas."""
    return df.drop(columns=["ID"], errors="ignore").reset_index(drop=True)


def plot_bar(df, x, y, title, color_scale="Viridis"):
    df_plot = clean_df(df)
    fig = px.bar(
        df_plot,
        x=x,
        y=y,
        orientation="h",
        text=x,
        color=x,
        color_continuous_scale=color_scale,
        title=title,
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig


# ------------------ Cache otimizado ------------------ #
@st.cache_data(show_spinner=True)
def carregar_analises_principais():
    """
    Carrega todos os datasets principais e já remove coluna ID desnecessária.
    """
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
    ) = inicializar_dados()

    # Remover coluna ID das análises
    for df in [correlacoes, comparativo, df_attr_geral]:
        if "ID" in df.columns:
            df.drop(columns=["ID"], inplace=True)

    correlacoes = correlacoes[correlacoes["Atributo"] != "ID"]
    comparativo = comparativo[comparativo["Atributo"] != "ID"]

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


@st.cache_data(show_spinner=True)
def carregar_combate_estatisticas():
    """
    Carrega combates e estatísticas com cache para acelerar filtros futuros.
    """
    df_combate = carregar_tabela("combates_com_nomes")
    df_estatisticas = carregar_tabela("estatisticas_pokemon")
    return df_combate, df_estatisticas


@st.cache_data(show_spinner=True)
def get_tipos(df_attr_geral):
    return sorted(df_attr_geral["Types"].dropna().unique())


@st.cache_data(show_spinner=True)
def get_pokemon_by_tipo(df_attr_geral, tipo):
    df_tipo = df_attr_geral[df_attr_geral["Types"] == tipo].copy()
    return clean_df(df_tipo)


@st.cache_data(show_spinner=True)
def get_pokemon_list(df_attr_geral):
    return sorted(df_attr_geral["Nome"].unique())


@st.cache_data(show_spinner=True)
def get_pokemon_attributes(df_attr_geral, pokemon_name):
    df_p = df_attr_geral[df_attr_geral["Nome"] == pokemon_name].copy()
    return clean_df(df_p)


# ------------------ Carregando dados ------------------ #
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
) = carregar_analises_principais()

df_combate, df_estatisticas = carregar_combate_estatisticas()


# ------------------ Layout em Tabs ------------------ #
tabs = st.tabs(
    [
        "Top10",
        "Atributos & Radar",
        "Correlação & Distribuição",
        "Ranking de Tipos",
        "Filtro por Tipo",
        "Comparação de Pokémon",
        "📖 Histórico de Batalhas",
    ]
)

# ------------------ Tab 1: Top10 ------------------ #
with tabs[0]:
    st.subheader("🏆 Top 10 Vitórias e Derrotas")
    col1, col2 = st.columns(2)
    if top10_vitorias is not None and not top10_vitorias.empty:
        with col1:
            st.plotly_chart(
                plot_bar(top10_vitorias, "Vitorias", "Pokemon", "Top 10 Vitórias"),
                use_container_width=True,
                config={"displayModeBar": False},
                key="top10_vitorias_plot",
            )
    if top10_derrotas is not None and not top10_derrotas.empty:
        with col2:
            st.plotly_chart(
                plot_bar(
                    top10_derrotas,
                    "Derrotas",
                    "Pokemon",
                    "Top 10 Derrotas",
                    color_scale="Reds",
                ),
                use_container_width=True,
                config={"displayModeBar": False},
                key="top10_derrotas_plot",
            )
    if top10_taxa is not None and not top10_taxa.empty:
        st.subheader("🔥 Top 10 por Taxa de Vitória (%)")
        st.plotly_chart(
            plot_bar(
                top10_taxa,
                "Taxa_Vitoria(%)",
                "Pokemon",
                "Top 10 Taxa de Vitória (%)",
                color_scale="Blues",
            ),
            use_container_width=True,
            config={"displayModeBar": False},
            key="top10_taxa_plot",
        )

# ------------------ Tab 2: Atributos & Radar ------------------ #
with tabs[1]:
    st.subheader("📊 Comparativo de Atributos Top10 vs Média Geral")
    if comparativo is not None and not comparativo.empty:
        df_comp = clean_df(comparativo)
        fig_radar = px.line_polar(
            df_comp,
            r="Média_Top10",
            theta="Atributo",
            line_close=True,
            title="Média Top10 vs Geral",
        )
        fig_radar.add_scatterpolar(
            r=df_comp["Média_Geral"],
            theta=df_comp["Atributo"],
            line=dict(color="red", dash="dash"),
            name="Média Geral",
        )
        st.plotly_chart(
            fig_radar,
            use_container_width=True,
            config={"displayModeBar": False},
            key="radar_comparativo_top10",
        )

# ------------------ Tab 3: Correlação & Distribuição ------------------ #
with tabs[2]:
    st.subheader("📈 Correlação de Atributos x Vitórias")
    if correlacoes is not None and not correlacoes.empty:
        df_corr = clean_df(correlacoes)
        fig_corr = px.bar(
            df_corr,
            x="Correlação_com_Vitórias",
            y="Atributo",
            orientation="h",
            text="Correlação_com_Vitórias",
            color="Correlação_com_Vitórias",
            color_continuous_scale="Cividis",
        )
        fig_corr.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(
            fig_corr,
            use_container_width=True,
            config={"displayModeBar": False},
            key="correlacoes_plot",
        )

    st.subheader("📊 Distribuição da Taxa de Vitória (%)")
    if distribuicao is not None and not distribuicao.empty:
        df_dist = clean_df(distribuicao)
        fig_dist = px.pie(
            df_dist,
            names="Faixa",
            values="Proporção(%)",
            color="Faixa",
            color_discrete_sequence=px.colors.sequential.RdBu,
        )
        st.plotly_chart(
            fig_dist,
            use_container_width=True,
            config={"displayModeBar": False},
            key="distribuicao_plot",
        )

# ------------------ Tab 4: Ranking de Tipos ------------------ #
with tabs[3]:
    st.subheader("🎨 Ranking de Tipos por Taxa de Vitória Média")
    if ranking_tipos is not None and not ranking_tipos.empty:
        st.plotly_chart(
            plot_bar(
                ranking_tipos,
                "media_taxa_vitoria",
                "Types",
                "Ranking de Tipos",
                color_scale="Viridis",
            ),
            use_container_width=True,
            config={"displayModeBar": False},
            key="ranking_tipos_plot",
        )

# ------------------ Tab 5: Filtro por Tipo ------------------ #
with tabs[4]:
    st.subheader("🔍 Filtrar Pokémon por Tipo")
    tipos = get_tipos(df_attr_geral)
    tipo_selecionado = st.selectbox("Selecione o tipo", tipos, key="select_tipo")
    df_attr_tipo = get_pokemon_by_tipo(df_attr_geral, tipo_selecionado)
    st.dataframe(
        df_attr_tipo[
            ["Nome", "Types"] + list(df_attr_tipo.select_dtypes("number").columns)
        ],
        use_container_width=True,
    )

# ------------------ Tab 6: Comparação de Dois Pokémon ------------------ #
with tabs[5]:
    st.subheader("⚡ Comparação Interativa de Dois Pokémon")
    pokemon_options = get_pokemon_list(df_attr_geral)
    col1, col2 = st.columns(2)
    with col1:
        pokemon1 = st.selectbox("Primeiro Pokémon", options=pokemon_options, key="p1")
    with col2:
        pokemon2 = st.selectbox("Segundo Pokémon", options=pokemon_options, key="p2")

    def radar_attributes(pokemon_name, suffix):
        df_p = get_pokemon_attributes(df_attr_geral, pokemon_name)
        col_num = df_p.select_dtypes(include="number").columns
        df_plot = pd.DataFrame(
            {
                "Atributo": col_num,
                "Valor do Pokémon": df_p[col_num].iloc[0],
                "Média Geral": df_attr_geral[col_num].mean(),
            }
        )
        fig = px.line_polar(
            df_plot,
            r="Valor do Pokémon",
            theta="Atributo",
            line_close=True,
            title=pokemon_name,
        )
        fig.add_scatterpolar(
            r=df_plot["Média Geral"],
            theta=df_plot["Atributo"],
            line=dict(color="red", dash="dash"),
            name="Média Geral",
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
            key=f"radar_{pokemon_name}_{suffix}",
        )

    radar_attributes(pokemon1, "1")
    radar_attributes(pokemon2, "2")

    def stat_box(pokemon_name):
        df_p = clean_df(df_estatisticas[df_estatisticas["Pokemon"] == pokemon_name])
        if df_p.empty:
            return None
        return df_p.iloc[0][["Vitorias", "Derrotas", "Taxa_Vitoria(%)"]]

    col1, col2 = st.columns(2)
    with col1:
        stats1 = stat_box(pokemon1)
        if stats1 is not None:
            st.metric(f"{pokemon1} - Vitórias", int(stats1["Vitorias"]))
            st.metric(f"{pokemon1} - Derrotas", int(stats1["Derrotas"]))
            st.metric(
                f"{pokemon1} - Taxa de Vitória (%)", float(stats1["Taxa_Vitoria(%)"])
            )
    with col2:
        stats2 = stat_box(pokemon2)
        if stats2 is not None:
            st.metric(f"{pokemon2} - Vitórias", int(stats2["Vitorias"]))
            st.metric(f"{pokemon2} - Derrotas", int(stats2["Derrotas"]))
            st.metric(
                f"{pokemon2} - Taxa de Vitória (%)", float(stats2["Taxa_Vitoria(%)"])
            )

    df_duelo = df_combate[
        (
            (df_combate["nome_first"] == pokemon1)
            & (df_combate["nome_second"] == pokemon2)
        )
        | (
            (df_combate["nome_first"] == pokemon2)
            & (df_combate["nome_second"] == pokemon1)
        )
    ]
    vitorias_p1 = (df_duelo["nome_winner"] == pokemon1).sum()
    vitorias_p2 = (df_duelo["nome_winner"] == pokemon2).sum()
    total_duelos = len(df_duelo)
    st.write(f"Total de combates entre {pokemon1} e {pokemon2}: {total_duelos}")
    st.write(f"{pokemon1} venceu {vitorias_p1} vezes")
    st.write(f"{pokemon2} venceu {vitorias_p2} vezes")

    if total_duelos > 0:
        df_duelo_plot = pd.DataFrame(
            {"Pokémon": [pokemon1, pokemon2], "Vitórias": [vitorias_p1, vitorias_p2]}
        )
        fig_duelo = px.pie(
            df_duelo_plot,
            names="Pokémon",
            values="Vitórias",
            title="Resultado dos Combates Diretos",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(
            fig_duelo,
            use_container_width=True,
            config={"displayModeBar": False},
            key=f"duelo_{pokemon1}_{pokemon2}",
        )

# ------------------ Tab 7: Histórico de Batalhas ------------------ #
with tabs[6]:
    st.subheader("📜 Histórico de Batalhas de um Pokémon")
    pokemon_options = get_pokemon_list(df_attr_geral)
    pokemon_escolhido = st.selectbox(
        "Selecione um Pokémon", pokemon_options, key="historico"
    )
    df_batalhas = clean_df(
        df_combate[
            (df_combate["nome_first"] == pokemon_escolhido)
            | (df_combate["nome_second"] == pokemon_escolhido)
        ]
    )

    if df_batalhas.empty:
        st.warning("⚠️ Nenhuma batalha encontrada para este Pokémon.")
    else:
        df_batalhas["Adversário"] = df_batalhas.apply(
            lambda row: row["nome_second"]
            if row["nome_first"] == pokemon_escolhido
            else row["nome_first"],
            axis=1,
        )
        df_batalhas["Resultado"] = df_batalhas.apply(
            lambda row: "Vitória"
            if row["nome_winner"] == pokemon_escolhido
            else "Derrota",
            axis=1,
        )
        st.markdown(f"### 🧩 {pokemon_escolhido} — Histórico de Combates")
        st.dataframe(
            df_batalhas[
                ["nome_first", "nome_second", "nome_winner", "Adversário", "Resultado"]
            ],
            hide_index=True,
            use_container_width=True,
        )

        total = len(df_batalhas)
        vitorias = (df_batalhas["Resultado"] == "Vitória").sum()
        derrotas = (df_batalhas["Resultado"] == "Derrota").sum()
        taxa = round((vitorias / total) * 100, 2) if total > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Batalhas", total)
        col2.metric("Vitórias", vitorias)
        col3.metric("Taxa de Vitória (%)", taxa)

        fig_pie = px.pie(
            pd.DataFrame(
                {
                    "Resultado": ["Vitórias", "Derrotas"],
                    "Quantidade": [vitorias, derrotas],
                }
            ),
            names="Resultado",
            values="Quantidade",
            title=f"Desempenho de {pokemon_escolhido}",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(
            fig_pie,
            use_container_width=True,
            config={"displayModeBar": False},
            key=f"historico_pie_{pokemon_escolhido}",
        )

st.markdown("---")
st.markdown(
    "Dashboard gerado automaticamente a partir do pipeline de análises Pokémon ⚡"
)
