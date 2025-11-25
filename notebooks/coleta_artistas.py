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

# 2- definir bandas seed

seed_artists_names = [
    'Mastodon',
    'Gojira',
    'Jinjer',
    'Tool',
    'Lacuna Coil'
]

print(f'Bandas seed: {seed_artists_names}')

# %%

# 3- buscar artistas seed + relacionados

all_artists = {}

for name in seed_artists_names:

    search_result = sp.search(q=name, type='artist', limit=1)
    items = search_result['artists']['items']

    if not items:
        print(f'Nenhum artista encontrado para: {name}')
        continue

    artist = items[0]
    artist_id = artist['id']

    all_artists[artist_id] = {
        'id': artist_id,
        'name': artist['name'],
        'popularity': artist['popularity'],
        'genres': artist['genres'],
        'spotify_url': artist['external_urls'].get('spotify', None)
    }

    try:
        related_data = sp.artist_related_artists(artist_id)
        related = related_data.get("artists", [])
    except spotipy.exceptions.SpotifyException as e:
        print(f"Nenhum artista relacionado encontrado para {name} (ID={artist_id})")
        print("Motivo:", e)
        continue


    for rel in related:
        rel_id = rel['id']

        if rel_id not in all_artists:
            all_artists[rel_id] = {
                'id': rel_id,
                'name': rel['name'],
                'popularity': rel['popularity'],
                'genres': rel['genres'],
                'spotify_url': rel['external_urls'].get('spotify',None)
            }


print(f'Total de artistas: {len(all_artists)}')



# %%
