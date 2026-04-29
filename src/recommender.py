import os
import sys

sys.path.append(os.path.abspath(".."))

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.features import get_genre_feature_matrix, BASE_COLS


def recommend_artists_by_genre(
    df_with_genres: pd.DataFrame,
    user_likes: list[str],
    top_k: int = 20,
    underground_weight: float = 0.3,
    max_listeners: int = 500_000,
) -> pd.DataFrame:
    """
    Gera recomendações de artistas com base em gêneros/tags e número
    inverso de listeners (fator underground).

    Parâmetros
    ----------
    df_with_genres : pandas.DataFrame
        DataFrame retornado por add_genre_vectors, com colunas binárias
        de gênero além das colunas base.

    user_likes : list[str]
        Nomes das bandas que o usuário informou gostar.

    top_k : int
        Número máximo de artistas recomendados a retornar.

    underground_weight : float
        Peso do fator underground no score final (0.0 a 1.0).
            0.0 → só similaridade de gêneros
            0.3 → 70% similaridade + 30% underground
            1.0 → só underground (não recomendado)

    max_listeners : int
        Artistas com listeners acima deste limite são descartados.
        Padrão: 500.000 (bandas muito populares tendem a estar acima disso).

    Retorno
    -------
    pandas.DataFrame
        DataFrame com as colunas originais mais:
            - similarity
            - listeners_norm
            - underground_score
            - final_score
        Ordenado por final_score (decrescente), sem incluir as bandas
        que o usuário já informou.
    """
    if df_with_genres.empty:
        print("DataFrame vazio, nada para recomendar.")
        return df_with_genres

    user_likes_lower = [n.lower().strip() for n in user_likes]

    liked_rows = df_with_genres[
        df_with_genres["name"].str.lower().isin(user_likes_lower)
    ]

    if liked_rows.empty:
        print("Nenhuma das bandas informadas foi encontrada no dataset.")
        return df_with_genres.iloc[0:0]

    X, genre_cols = get_genre_feature_matrix(df_with_genres)

    # Perfil do usuário: média dos vetores de gênero das bandas que ele gosta
    user_profile = liked_rows[genre_cols].values.mean(axis=0, keepdims=True)

    # Similaridade de cosseno entre perfil e todos os artistas
    sims = cosine_similarity(user_profile, X)[0]

    df_scores = df_with_genres.copy()
    df_scores["similarity"] = sims

    # Normaliza listeners para [0, 1]
    max_list = df_scores["listeners"].max() or 1
    df_scores["listeners_norm"] = df_scores["listeners"] / max_list

    # Fator underground: quanto menos ouvintes, maior o score
    df_scores["underground_score"] = 1 - df_scores["listeners_norm"]

    # Score final combinado
    w_sim = 1.0 - underground_weight
    w_und = underground_weight
    df_scores["final_score"] = (
        w_sim * df_scores["similarity"] + w_und * df_scores["underground_score"]
    )

    # Filtros
    df_scores = df_scores[df_scores["listeners"] <= max_listeners]
    df_scores = df_scores[df_scores["similarity"] > 0]
    df_scores = df_scores[
        ~df_scores["name"].str.lower().isin(user_likes_lower)
    ]

    df_scores = df_scores.sort_values("final_score", ascending=False)
    return df_scores.head(top_k)