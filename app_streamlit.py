import os
import sys

sys.path.append(os.path.abspath(".."))

import pandas as pd
import streamlit as st

from src.dataset import expand_artists_from_user_likes
from src.recommender import recommend_artists_by_genre
from src.cache.cache_db import init_db

init_db()

# --------------------------------------------------------------------------- #
#  Configuração da página                                                      #
# --------------------------------------------------------------------------- #

st.set_page_config(
    page_title="Metal Underground Recommender",
    page_icon="🤘",
    layout="wide",
)

st.title("🤘 Metal Underground Recommender")
st.markdown(
    """
Recomendador de bandas underground baseado nos seus gostos, usando a API da **Last.fm**.

1. Digite bandas que você gosta (separadas por vírgula).
2. O sistema busca artistas relacionados por similaridade e por tags/gêneros.
3. Gera recomendações priorizando bandas menos populares, mas sonoramente próximas.
"""
)

# --------------------------------------------------------------------------- #
#  Entrada do usuário                                                          #
# --------------------------------------------------------------------------- #

band_input = st.text_input(
    "Quais bandas você gosta?",
    value="Gojira, Mastodon",
    help="Digite nomes separados por vírgula, ex: Gojira, Mastodon, Jinjer",
)

col1, col2, col3 = st.columns(3)

with col1:
    top_k = st.number_input(
        "Quantas recomendações?",
        min_value=5,
        max_value=50,
        value=15,
        step=1,
    )

with col2:
    underground_weight = st.slider(
        'Peso do "underground" no score',
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
        help="0 = só similaridade de tags, 1 = só quão pouco popular é.",
    )

with col3:
    max_listeners = st.number_input(
        "Listeners máximos (Last.fm)",
        min_value=10_000,
        max_value=5_000_000,
        value=500_000,
        step=50_000,
        help="Bandas com mais ouvintes do que isso serão descartadas.",
        format="%d",
    )

# --------------------------------------------------------------------------- #
#  Cache de recursos                                                           #
# --------------------------------------------------------------------------- #

@st.cache_data(show_spinner=True)
def build_universe(
    user_likes: tuple[str, ...],
    max_similar: int = 30,
    max_per_tag: int = 20,
) -> pd.DataFrame:
    """
    Expande o universo de artistas via Last.fm e retorna o DataFrame
    com vetores de gênero prontos para recomendação.

    O resultado é cacheado pelo Streamlit enquanto os parâmetros
    não mudarem.
    """
    return expand_artists_from_user_likes(
        user_likes=list(user_likes),
        max_similar=max_similar,
        max_per_tag=max_per_tag,
    )

# --------------------------------------------------------------------------- #
#  Execução                                                                    #
# --------------------------------------------------------------------------- #

if st.button("Gerar recomendações"):
    if not band_input.strip():
        st.warning("Por favor, digite ao menos uma banda.")
        st.stop()

    user_likes = [b.strip() for b in band_input.split(",") if b.strip()]

    if not user_likes:
        st.warning("Não consegui entender nenhuma banda no input 😅")
        st.stop()

    st.write("**Bandas informadas:**", ", ".join(user_likes))

    with st.spinner("Buscando artistas similares na Last.fm..."):
        df_with_genres = build_universe(tuple(user_likes))

    if df_with_genres.empty:
        st.error("Não consegui montar um universo de artistas a partir dessas bandas.")
        st.stop()

    st.success(f"Universo de artistas montado: {len(df_with_genres)} artistas.")

    with st.spinner("Calculando recomendações..."):
        recs = recommend_artists_by_genre(
            df_with_genres=df_with_genres,
            user_likes=user_likes,
            top_k=top_k,
            underground_weight=underground_weight,
            max_listeners=max_listeners,
        )

    if recs.empty:
        st.warning(
            "Nenhuma recomendação encontrada com os filtros atuais. "
            "Tente aumentar o limite de listeners ou diminuir o peso do underground."
        )
        st.stop()

    # ----------------------------------------------------------------------- #
    #  Resultados                                                              #
    # ----------------------------------------------------------------------- #

    st.subheader("🎸 Recomendações")

    cols_to_show = [
        c for c in ["name", "genres", "listeners", "similarity",
                    "underground_score", "final_score", "lastfm_url"]
        if c in recs.columns
    ]

    display_df = recs[cols_to_show].copy().reset_index(drop=True)

    if "genres" in display_df.columns:
        display_df["genres"] = display_df["genres"].apply(
            lambda g: ", ".join(g) if isinstance(g, list) else str(g)
        )

    if "listeners" in display_df.columns:
        display_df["listeners"] = display_df["listeners"].apply(
            lambda x: f"{int(x):,}" if pd.notna(x) else "—"
        )

    for score_col in ["similarity", "underground_score", "final_score"]:
        if score_col in display_df.columns:
            display_df[score_col] = display_df[score_col].apply(
                lambda x: f"{x:.3f}" if pd.notna(x) else "—"
            )

    column_config = {}
    if "lastfm_url" in display_df.columns:
        column_config["lastfm_url"] = st.column_config.LinkColumn(
            "Link na Last.fm",
            display_text="Abrir na Last.fm",
        )

    st.dataframe(
        display_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(f"Exibindo {len(recs)} recomendações.")

else:
    st.info("Digite as bandas que você gosta e clique em **Gerar recomendações**.")