#%%

import spotipy
import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import ast

#%%

def get_artist_by_name(sp, name):
    res = sp.search(q=name, type="artist", limit=1)
    items = res["artists"]["items"]
    return items[0] if items else None

# %%

def collect_seed_artists(sp, seed_artists_names):
    
    all_artists = {}

    print("\n=== Buscando artistas seed no Spotify ===")

    for name in seed_artists_names:
        print(f'\n>>>Procurando: {name}')

        try:
            search_result = sp.search(q=name, type='artist', limit=1)
        except spotipy.exceptions.SpotifyException as e:
            print(f'Erro na busca do Spotify ao buscar {name}: {e}')
            continue
        except Exception as e:
            print(f'Erro inesperado ao buscar {name}: {e}')
            continue

        
        items = search_result['artists']['items']

        if not items:
            print(f'Nenhum artista encontrado para: {name}')
            continue

        artist = items[0]
        artist_id = artist['id']

        if artist_id in all_artists:
            print(f'{artist["name"]} (ID já existe), pulando.')
            continue

        asrtist_info = {
            'id': artist_id,
            'name': artist['name'],
            'popularity': artist['popularity'],
            'genres': artist['genres'],
            'spotify_url': artist['external_urls'].get('spotify', None)
        }

        all_artists[artist_id] = asrtist_info

        print(f'Artista encontrado: {artist["name"]} (ID={artist_id})')
        print(f'Popularidade: {artist["popularity"]}')
        print(f'Gêneros: {artist["genres"]}')

    print(f"\nTotal de artistas seed encontrados (sem duplicata): {len(all_artists)}")
    return all_artists

# %%

BASE_COLS = ['id', 'name', 'popularity', 'genres', 'spotify_url']

#%%

def _normalize_genres(value):
    if isinstance(value, list):
        return value
    
    if pd.isna(value):
        return []
    
    if isinstance(value, str):
        text = value.strip()
        if text == "" or text.lower() == "nan":
            return []
        
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                # garantir que tudo é str e sem espaços extras
                return [str(x).strip() for x in parsed]
        except Exception:
            pass
        
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1].strip()
        
        parts = [s.strip() for s in text.split(",") if s.strip()]

        return parts
        
    return []

# %%

def add_genre_vectors(df_artists: pd.DataFrame):

    df = df_artists.copy()
    df['genres'] = df['genres'].apply(_normalize_genres) 

    print("Exemplos de genres normalizados:")
    print(df["genres"].head())

    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(df['genres'])

    print(f"\nTotal de gêneros distintos encontrados: {len(mlb.classes_)}")
    if len(mlb.classes_) > 0:
        print("Alguns gêneros:", mlb.classes_[:10])

    genre_df = pd.DataFrame(
        genre_matrix,
        columns=mlb.classes_,
        index=df.index
    )

    df_with_genres = pd.concat([df, genre_df], axis=1)

    return df_with_genres, mlb

# %%

def get_genre_feature_matrix(df_with_genres: pd.DataFrame):
    genre_cols = [c for c in df_with_genres.columns if c not in BASE_COLS]
    X = df_with_genres[genre_cols].values
    return X, genre_cols

# %%
