#%%

import spotipy
import numpy as np

#%%

AUDIO_FEATURES = [
    'acousticness',
    'danceability',
    'energy',
    'instrumentalness',
    'liveness',
    'speechiness',
    'valence',
    'tempo'
]

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

def get_artist_vector(sp, artist_id: str, country: str = 'US'):
    try:
        top = sp.artist_top_tracks(artist_id, country=country)['tracks']
    except Exception as e:
        print(f'Erro ao buscar top tracks do artista {artist_id}: {e}')
        return None
    
    track_ids = [t['id'] for t in top]
    if not track_ids:
        print(f'Artista {artist_id} não tem top tracks.')
        return None
    
    try:
        feats = sp.audio_features(track_ids)
    except Exception as e:
        print(f'Erro ao buscar audio_features do artista {artist_id}: {e}')
        return None
    
    feats = [f for f in feats if f is not None]
    if not feats:
        print(f'Sem audio_features válidas para {artist_id}.')
        return None
    
    try:
        matrix = np.array([
            [f[feat] for feat in AUDIO_FEATURES]
            for f in feats
        ])
    except KeyError as e:
        print(f'Feature faltando para {artist_id}: {e}.')
        return None
    
    mean_vector = matrix.mean(axis=0)
    return mean_vector

# %%
