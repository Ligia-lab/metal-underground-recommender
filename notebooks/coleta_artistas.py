#%%

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
import pandas as pd


# %%

# 1- autenticação
load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)

sp = spotipy.Spotify(auth_manager=auth_manager)

print(sp is not None)

# %%

# 2- buscar artistas seed 

seed_artists_names = [
    'Mastodon',
    'Gojira',
    'Jinjer',
    'Tool',
    'Lacuna Coil'
]

print(f'Bandas seed: {seed_artists_names}')

all_artists = {}

print("\n=== Buscando artistas seed no Spotify ===")

for name in seed_artists_names:
    print(f'\n>>>Procurando: {name}')

    try:
        search_result = sp.search(q=name, type='artist', limit=1)
    except Exception as e:
        print(f'Erro ao buscar {name}: {e}')
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

    all_artists[artist_id] = {
        'id': artist_id,
        'name': artist['name'],
        'popularity': artist['popularity'],
        'genres': artist['genres'],
        'spotify_url': artist['external_urls'].get('spotify', None)
    }

    print(f"Artista encontrado: {artist['name']} (ID={artist_id})")
    print(f"Popularidade: {artist['popularity']}, Gêneros: {artist['genres']}")

print(f"\nTotal de artistas seed encontrados (sem duplicata): {len(all_artists)}")

# %%
