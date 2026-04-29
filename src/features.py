import ast
import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity

# Colunas base do DataFrame (não são colunas de gênero)
BASE_COLS = ["name", "listeners", "genres", "lastfm_url"]


# --------------------------------------------------------------------------- #
#  Normalização de gêneros                                                     #
# --------------------------------------------------------------------------- #

def _normalize_genres(value) -> list[str]:
    """
    Normaliza o conteúdo da coluna 'genres' para garantir que sempre seja
    retornada uma lista de strings.

    Trata os seguintes formatos de entrada:
        - Lista real               : ['progressive metal', 'sludge metal']
        - String de lista Python   : "['progressive metal', 'sludge metal']"
        - String separada por vírgula: "progressive metal, sludge metal"
        - Valor vazio / NaN        : retorna []

    Parâmetros
    ----------
    value : qualquer tipo
        Valor da coluna 'genres'.

    Retorno
    -------
    list[str]
        Lista de gêneros normalizados.
    """
    if isinstance(value, list):
        return [str(x).strip().lower() for x in value if str(x).strip()]

    if pd.isna(value):
        return []

    if isinstance(value, str):
        text = value.strip()
        if not text or text.lower() == "nan":
            return []

        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return [str(x).strip().lower() for x in parsed if str(x).strip()]
        except Exception:
            pass

        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1].strip()

        return [s.strip().lower() for s in text.split(",") if s.strip()]

    return []


# --------------------------------------------------------------------------- #
#  Vetorização de gêneros                                                      #
# --------------------------------------------------------------------------- #

def add_genre_vectors(df_artists: pd.DataFrame):
    """
    Converte a coluna 'genres' em vetores numéricos usando MultiLabelBinarizer,
    criando uma coluna binária (0/1) para cada tag/gênero encontrado.

    Parâmetros
    ----------
    df_artists : pandas.DataFrame
        DataFrame contendo pelo menos a coluna 'genres'.

    Retorno
    -------
    tuple
        df_with_genres : pandas.DataFrame
            DataFrame original acrescido de colunas binárias por gênero.
        mlb : MultiLabelBinarizer
            Codificador treinado (útil para interpretar as classes depois).
    """
    df = df_artists.copy()
    df["genres"] = df["genres"].apply(_normalize_genres)

    print("Exemplos de genres normalizados:")
    print(df["genres"].head())

    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(df["genres"])

    print(f"\nTotal de gêneros/tags distintos encontrados: {len(mlb.classes_)}")
    if len(mlb.classes_) > 0:
        print("Alguns gêneros:", mlb.classes_[:10])

    genre_df = pd.DataFrame(
        genre_matrix,
        columns=mlb.classes_,
        index=df.index,
    )

    df_with_genres = pd.concat([df, genre_df], axis=1)
    return df_with_genres, mlb


# --------------------------------------------------------------------------- #
#  Extração da matriz de features                                              #
# --------------------------------------------------------------------------- #

def get_genre_feature_matrix(df_with_genres: pd.DataFrame):
    """
    Extrai do DataFrame as colunas de gênero (binárias) e retorna a matriz
    numérica de features junto com os nomes das colunas.

    Parâmetros
    ----------
    df_with_genres : pandas.DataFrame
        DataFrame retornado por add_genre_vectors.

    Retorno
    -------
    tuple
        X : numpy.ndarray
            Matriz (n_artistas × n_gêneros) com valores 0/1.
        genre_cols : list[str]
            Nomes das colunas de gênero usadas na matriz X.
    """
    genre_cols = [c for c in df_with_genres.columns if c not in BASE_COLS]
    X = df_with_genres[genre_cols].values
    return X, genre_cols