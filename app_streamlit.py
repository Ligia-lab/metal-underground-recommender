

import os
import sys

sys.path.append(os.path.abspath(".."))

import pandas as pd
import streamlit as st
from src.spotify_client import get_spotify_client
from src.dataset import expand_artists_from_user_likes
from src.recommender import recommend_artists_by_genre



#TÍTULO

st.set_page_config(page_title='Metal Underground Recommender',
                   page_icon='🤘',
                   layout='wide')

st.title('🤘 Metal Underground Recommender')
st.markdown(
    """
Recomendador de bandas underground baseado nos seus gostos, usando a API do Spotify.

1. Digite bandas que você gosta (separadas por vírgula).
2. O sistema busca artistas relacionados e por gêneros.
3. Gera recomendações priorizando bandas menos populares, mas semelhantes.
"""
)



#ENTRADA DO USUÁRIO

band_input = st.text_input('Quais bandas você gosta?',
                           value='Gojira, Mastodon',
                           help='Digite nomes separados por vírgula, ex: Gojira, Mastodon, Jinjer')


col1, col2, col3 = st.columns(3)

with col1:
    top_k = st.number_input('Quantas recomendações?',
        min_value=5,
        max_value=50,
        value=15,
        step=1
    )

with col2:
    underground_weight = st.slider(
        'Peso do "underground" no score',
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
        help='0 = só similaridade de gêneros, 1 = só quão pouco popular é.'
    )

with col3:
    max_popularity = st.slider(
        'Popularidade máxima (Spotify)',
        min_value=10,
        max_value=100,
        value=50,
        step=5,
        help='Bandas com popularidade acima disso serão descartadas.'
    )




#FUNÇÕES CACHED

@st.cache_resource(show_spinner=False)
def get_spotify_client_cached():
    return get_spotify_client()


@st.cache_data(show_spinner=True)
def build_universe(user_likes: list[str], max_related=30, max_per_genre_search=30):
    """
    Usa a API do Spotify para expandir o universo de artistas a partir
    das bandas que o usuário gosta. Retorna df_with_genres.
    """
    sp = get_spotify_client_cached()
    df_with_genres = expand_artists_from_user_likes(
        sp,
        user_likes=user_likes,
        max_related=max_related,
        max_per_genre_search=max_per_genre_search,
    )
    return df_with_genres


def apply_max_popularity_filter(df: pd.DataFrame, max_pop: int) -> pd.DataFrame:
    """
    Aplica filtro de popularidade máxima manualmente,
    caso a função de recomendação ainda tenha isso fixo.
    """
    if 'popularity' not in df.columns:
        return df
    return df[df['popularity'] <= max_pop]



#RODAR

if st.button('Gerar recomendações'):
    if not band_input.strip():
        st.warning('Por favor, digite ao menos uma banda.')
        st.stop()

    user_likes = [b.strip() for b in band_input.split(",") if b.strip()]

    if not user_likes:
        st.warning('Não consegui entender nenhuma banda no input 😅')
        st.stop()

    st.write('**Bandas informadas**', ', '.join(user_likes))

    with st.spinner('Buscando artistas similares no spotify....'):
        df_with_genres = build_universe(user_likes)

    if df_with_genres.empty:
        st.error('Não consegui montar um universo de artistas a partir dessas bandas.')
        st.stop()

    st.success(f'Universo de artistas montado.')


    with st.spinner('Calculando recomendações....'):
        recs = recommend_artists_by_genre(
            df_with_genres=df_with_genres,
            user_likes=user_likes,
            top_k=top_k,
            underground_weight=underground_weight
        )

        recs = apply_max_popularity_filter(recs, max_popularity)

    if recs.empty:
        st.warning("Nenhuma recomendação encontrada com os filtros atuais. "
                   "Tente aumentar a popularidade máxima ou diminuir o peso do underground.")
        st.stop()



#RESULTADOS

    st.subheader("🎸 Recomendações")

    cols_to_show = []
    for col in ["name", "genres", "popularity", "similarity", "underground_score", "final_score", "spotify_url"]:
        if col in recs.columns:
            cols_to_show.append(col)

    if 'genres' in recs.columns:
        recs = recs.copy()
        recs['genres'] = recs['genres'].apply(
            lambda g: ', '.join(g) if isinstance(g, list) else str(g)
        )

    st.dataframe(
        recs[cols_to_show].reset_index(drop=True),
        column_config={
            "spotify_url": st.column_config.LinkColumn(
                "Link no Spotify", 
                display_text="Abrir no Spotify" 
            )
        },
        use_container_width=True,
        hide_index=True
    )

    st.caption(f"Total de recomendações possíveis (antes de limitar em top_k): {len(recs)}")

else:
    st.info("Digite as bandas que você gosta e clique em **Gerar recomendações**.")
