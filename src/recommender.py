#%%

import os
import sys

sys.path.append(os.path.abspath(".."))

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.features import get_genre_feature_matrix, BASE_COLS

# %%

def recommend_artists_by_genre(df_with_genres: pd.DataFrame,
                               user_likes: list[str],
                               top_k: int = 20,
                               underground_weight: float = 0.3):
    """
    Gera recomendações de artistas com base em gêneros musicais e popularidade inversa.

    Parâmetros
    ----------
    df_with_genres : pandas.DataFrame
        DataFrame retornado por `add_genre_vectors`, contendo colunas de gêneros (0/1)
        além das colunas base (id, name, popularity, genres, spotify_url).

    user_likes : list[str]
        Lista de nomes de bandas/artistas que o usuário informou que gosta.

    top_k : int, opcional (default=20)
        Número de artistas recomendados a serem retornados.

    underground_weight : float, opcional (default=0.3)
        Peso do fator "underground" no score final.
        - 0.0  → só similaridade de gêneros
        - 0.3  → mistura 70% similaridade + 30% “quanto menos popular, melhor”
        - 1.0  → só “quanto menos popular, melhor” (não recomendado)

    Retorno
    -------
    pandas.DataFrame
        DataFrame com as colunas originais +:
            - similarity
            - pop_norm
            - underground_score
            - final_score
        filtrado para não incluir os artistas que o usuário já informou
        e ordenado por `final_score` (decrescente).
    """
    if df_with_genres.empty:
        print('DataFrame vazio, nada para recomendar')
        return df_with_genres
    
    #normalizar nomes de entrada
    user_likes_lower = [n.lower().strip() for n in user_likes]

    #selecionar linhas dos artistas que o usuário gosta
    liked_rows = df_with_genres[df_with_genres['name'].str.lower().isin(user_likes_lower)]

    if liked_rows.empty:
        print('Nenhuma das bandas informadas foi encontrada no dataset')
        return df_with_genres.iloc[0:0]
    
    #matriz de features de generos e nomes das cols de genero
    X, genre_cols = get_genre_feature_matrix(df_with_genres)

    #vetor de perfil do usuário: média dos vetores de genero das bandas liked
    user_profile = liked_rows[genre_cols].values.mean(axis=0, keepdims=True)

    #similaridade de cosseno entre perfil e todos os artistas
    sims = cosine_similarity(user_profile, X)[0]

    df_scores = df_with_genres.copy()
    df_scores['similarity'] = sims

    #normalizar popularidade para 0, 1
    max_pop = df_scores['popularity'].max() or 1
    df_scores['pop_norm'] = df_scores['popularity'] / max_pop

    #fator underground
    df_scores['underground_score'] = 1 - df_scores['pop_norm']

    #score final: similaridade + underground
    w_sim = 1.0 - underground_weight
    w_und = underground_weight

    df_scores['final_score'] = (
        w_sim * df_scores['similarity'] + w_und * df_scores['underground_score']
    )

    #remover bandas com popularidade acima de 50
    df_scores = df_scores[df_scores['popularity'] <= 55]

    #remover bandas sem similaridade
    df_scores = df_scores[df_scores['similarity'] > 0]

    #remover bandas que o usuário ja informou
    df_scores = df_scores[~df_scores['name'].str.lower().isin(user_likes_lower)]

    #ordenar por score final e limitar ao top_k
    df_scores = df_scores.sort_values('final_score', ascending=False)

    return df_scores.head(top_k)


# %%
