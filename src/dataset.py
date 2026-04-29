import os
import sys

sys.path.append(os.path.abspath(".."))

import pandas as pd
from src.lastfm_client import lastfm_get
from src.features import add_genre_vectors


# --------------------------------------------------------------------------- #
#  Funções de busca na API Last.fm                                             #
# --------------------------------------------------------------------------- #

def get_artist_info(artist_name: str) -> dict | None:
    """
    Busca informações completas de um artista na Last.fm usando
    o método artist.getInfo.

    Retorna um dicionário padronizado com:
        - name        : nome canônico do artista
        - listeners   : número de ouvintes únicos (substitui 'popularity')
        - genres      : lista de tags/gêneros (ordenadas por relevância)
        - lastfm_url  : URL do artista na Last.fm

    Parâmetros
    ----------
    artist_name : str
        Nome do artista a ser buscado.

    Retorno
    -------
    dict ou None
        Dicionário com dados do artista, ou None se não encontrado / erro.
    """
    try:
        data = lastfm_get("artist.getInfo", {"artist": artist_name})
    except Exception as e:
        print(f"  Erro ao buscar '{artist_name}': {e}")
        return None

    if "error" in data:
        print(f"  Last.fm erro {data['error']}: {data.get('message', '')} para '{artist_name}'")
        return None

    artist = data.get("artist", {})
    if not artist:
        return None

    stats = artist.get("stats", {})
    try:
        listeners = int(stats.get("listeners", 0))
    except (ValueError, TypeError):
        listeners = 0

    tags_raw = artist.get("tags", {}).get("tag", [])
    if isinstance(tags_raw, dict):
        tags_raw = [tags_raw]
    tags = [t["name"].lower().strip() for t in tags_raw if t.get("name")]

    return {
        "name": artist.get("name", artist_name),
        "listeners": listeners,
        "genres": tags,
        "lastfm_url": artist.get("url", ""),
    }


def get_similar_artists(artist_name: str, limit: int = 30) -> list[dict]:
    """
    Busca artistas similares via artist.getSimilar.

    Parâmetros
    ----------
    artist_name : str
        Nome do artista de referência.
    limit : int
        Número máximo de artistas similares a buscar.

    Retorno
    -------
    list[dict]
        Lista de dicionários com dados dos artistas similares.
    """
    try:
        data = lastfm_get("artist.getSimilar", {
            "artist": artist_name,
            "limit": limit,
        })
    except Exception as e:
        print(f"  Erro ao buscar similares de '{artist_name}': {e}")
        return []

    if "error" in data:
        print(f"  Last.fm erro {data['error']}: similares de '{artist_name}'")
        return []

    similar_raw = data.get("similarartists", {}).get("artist", [])
    if isinstance(similar_raw, dict):
        similar_raw = [similar_raw]

    results = []
    for item in similar_raw:
        name = item.get("name", "")
        if not name:
            continue
        info = get_artist_info(name)
        if info and info["genres"]:
            results.append(info)

    return results


def get_artists_by_tag(tag: str, limit: int = 20) -> list[dict]:
    """
    Busca top artistas de uma tag/gênero via tag.getTopArtists.

    Parâmetros
    ----------
    tag : str
        Nome da tag (ex: 'progressive metal', 'death metal').
    limit : int
        Número máximo de artistas a retornar.

    Retorno
    -------
    list[dict]
        Lista de dicionários com dados dos artistas encontrados.
    """
    try:
        data = lastfm_get("tag.getTopArtists", {
            "tag": tag,
            "limit": limit,
        })
    except Exception as e:
        print(f"  Erro ao buscar artistas por tag '{tag}': {e}")
        return []

    if "error" in data:
        print(f"  Last.fm erro {data['error']}: tag '{tag}'")
        return []

    artists_raw = data.get("topartists", {}).get("artist", [])
    if isinstance(artists_raw, dict):
        artists_raw = [artists_raw]

    results = []
    for item in artists_raw:
        name = item.get("name", "")
        if not name:
            continue
        info = get_artist_info(name)
        if info and info["genres"]:
            results.append(info)

    return results


# --------------------------------------------------------------------------- #
#  Construção do DataFrame                                                     #
# --------------------------------------------------------------------------- #

def build_basic_artists_df(all_artists: dict) -> pd.DataFrame:
    """
    Converte o dicionário de artistas coletados em um DataFrame pandas.

    Parâmetros
    ----------
    all_artists : dict
        Dicionário {artist_key: {name, listeners, genres, lastfm_url}}.

    Retorno
    -------
    pandas.DataFrame
        DataFrame com colunas: name, listeners, genres, lastfm_url.
    """
    records = list(all_artists.values())
    df = pd.DataFrame(records)
    return df


def expand_artists_from_user_likes(
    user_likes: list[str],
    max_similar: int = 30,
    max_per_tag: int = 20,
) -> pd.DataFrame:
    """
    Expande o universo de artistas a partir das bandas que o usuário gosta,
    usando a API da Last.fm.

    Estratégia de expansão (por artista informado):
        1. Busca informações do artista (tags/gêneros e listeners).
        2. Busca artistas similares via artist.getSimilar.
        3. Para cada tag do artista, busca os top artistas da tag.

    Retorna um DataFrame com colunas de gênero one-hot (0/1) prontas
    para o sistema de recomendação.

    Parâmetros
    ----------
    user_likes : list[str]
        Lista de nomes de bandas informadas pelo usuário.
    max_similar : int
        Máximo de artistas similares por banda base.
    max_per_tag : int
        Máximo de artistas por tag buscada.

    Retorno
    -------
    pandas.DataFrame
        DataFrame com artistas e colunas de gênero binárias.
    """
    all_artists: dict[str, dict] = {}

    def add_artist(info: dict):
        key = info["name"].lower().strip()
        if key not in all_artists:
            all_artists[key] = info

    print("\n=== Expandindo artistas a partir do gosto do usuário ===")

    for name in user_likes:
        print(f"\n>>> Buscando artista base: {name}")

        artist = get_artist_info(name)
        if artist is None:
            print(f"  Nenhum artista encontrado para: {name}")
            continue

        add_artist(artist)
        print(f"  Tags: {artist['genres']}")
        print(f"  Listeners: {artist['listeners']:,}")

        # Artistas similares
        print(f"  Buscando similares...")
        similar = get_similar_artists(name, limit=max_similar)
        for a in similar:
            add_artist(a)
        print(f"  {len(similar)} similares adicionados.")

        # Artistas por tag
        for tag in artist["genres"]:
            print(f"  Buscando artistas pela tag: {tag}")
            tag_artists = get_artists_by_tag(tag, limit=max_per_tag)
            for a in tag_artists:
                add_artist(a)

    print(f"\nTotal de artistas coletados: {len(all_artists)}")

    df_artists = build_basic_artists_df(all_artists)
    df_with_genres, _ = add_genre_vectors(df_artists)
    df_with_genres = df_with_genres[df_with_genres["genres"].apply(len) > 0]

    return df_with_genres