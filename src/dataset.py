#%%

import os
import sys

sys.path.append(os.path.abspath(".."))

import pandas as pd
import spotipy
from src.features import get_artist_by_name, add_genre_vectors

# %%

def build_basic_artists_df(all_artists: dict):
    """
    Constrói um DataFrame pandas contendo as informações essenciais de artistas
    coletados previamente pela função `collect_seed_artists`.

    Objetivo da função
    -------------------
    Transformar o dicionário retornado pela etapa de coleta de artistas
    (onde cada chave é um `artist_id` e o valor é um dicionário com dados
    do artista) em um DataFrame tabular e organizado, adequado para análise
    e pré-processamento.

    O que esta função faz?
    -----------------------
    1) Recebe um dicionário no formato:
        {
            artist_id: {
                'id': str,
                'name': str,
                'popularity': int,
                'genres': list[str],
                'spotify_url': str
            },
            ...
        }

    2) Converte cada entrada do dicionário em um registro (linha) para o DataFrame.
    3) Retorna um DataFrame pandas com as colunas:
         - id
         - name
         - popularity
         - genres
         - spotify_url

    Parâmetros
    ----------
    all_artists : dict
        Dicionário gerado por `collect_seed_artists`, contendo informações
        estruturadas sobre artistas únicos.

    Retorno
    -------
    pandas.DataFrame
        DataFrame contendo uma linha para cada artista encontrado.

    Exemplo
    -------
    Entrada:
        {
            "12345": {
                "id": "12345",
                "name": "Gojira",
                "popularity": 63,
                "genres": ["progressive metal", "groove metal"],
                "spotify_url": "https://open.spotify.com/artist/12345"
            }
        }

    Saída:
        id      | name   | popularity | genres                               | spotify_url
        --------+--------+------------+---------------------------------------+------------------------
        12345   | Gojira | 63         | ['progressive metal', 'groove metal'] | https://open.spotify...

    Observações
    -----------
    - Esta função não altera o dicionário original.
    - É uma etapa intermediária antes de aplicar vetorização de gêneros.

    """
    records = []

    for artist_id, info in all_artists.items():
        records.append({
            'id': info['id'],
            'name': info['name'],
            'popularity': info['popularity'],
            'genres': info['genres'],
            'spotify_url': info['spotify_url']
        })

    df = pd.DataFrame(records)
    return df

# %%

def expand_artists_from_user_likes(sp: spotipy.Spotify,
                                   user_likes: list[str],
                                   max_related: int = 20,
                                   max_per_genre_search: int = 20):
    """
    Expande o universo de artistas a partir das bandas que o usuário gosta,
    usando a API do Spotify (related artists + busca por gênero).

    Retorna:
        df_with_genres : DataFrame com artistas (likes + relacionados),
                         já com colunas de gêneros 0/1 prontas para recomendação.
    """
    all_artists = {}

    print("\n=== Expandindo artistas a partir do gosto do usuário ===")

    for name in user_likes:
        print(f'\n>>>Buscando artista base: {name}')
        artist = get_artist_by_name(sp, name)

        if artist is None:
            print(f'  Nenhum artista encontrado para: {name}')
            continue

        artist_id = artist['id']

        #add o artista que o usuário gosta
        def add_artist(a):
            a_id = a['id']
            if a_id not in all_artists:
                all_artists[a_id] = {
                    'id': a_id,
                    'name': a['name'],
                    'popularity': a['popularity'],
                    'genres': a['genres'],
                    'spotify_url': a['external_urls'].get('spotify', None)
                }
        
        add_artist(artist)

        #tenta pegar artistas relacionados
        try:
            related_data = sp.artist_related_artists(artist_id)
            related = related_data.get('artists', [])
            print(f'  {len(related)} artistas relacionados encontrados')
        except spotipy.exceptions.SpotifyException as e:
            print(f'  Não foi possível buscar related artists de {name}: {e}')
            related = []

        for rel in related[:max_related]:
            add_artist(rel)

        #para cada genero de artista buscar mais artista por genero
        for g in artist.get('genres', []):
            print(f'  Buscando artistas pelo gênero: {g}')
            try:
                search_res = sp.search(q=f'genre:"{g}"', type='artist', limit=max_per_genre_search)
                genre_artists = search_res['artists']['items']
            except spotipy.exceptions.SpotifyException as e:
                print(f'  Erro ao buscar por gênero {g}: {e}')
                continue

            for a in genre_artists:
                add_artist(a)


    print(f'\nTotal de artistas coletados: {len(all_artists)}')     

    #transforma dicionario em DF basico
    df_artists = build_basic_artists_df(all_artists)

    #adiciona colunas de generos 0/1
    df_with_genres, mlb = add_genre_vectors(df_artists)

    return df_with_genres


# %%
