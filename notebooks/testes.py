#%%

import os
import sys
from src.spotify_client import get_spotify_client
from src.features import get_artist_by_name, collect_seed_artists

#%%

# adiciona a pasta raiz do projeto ao PYTHONPATH

sys.path.append(os.path.abspath(".."))

sp = get_spotify_client()
results = sp.search(q='Mastodon', type='artist', limit=1)
results['artists']['items'][0]['name'], results['artists']['items'][0]['id']

# %%

artist = get_artist_by_name(sp, "Mastodon")

if artist is None:
    print("Não encontrou o artista.")
else:
    print("Nome :", artist["name"])
    print("ID   :", artist["id"])
    print("Pop  :", artist["popularity"])
    print("Genres:", artist["genres"])

# %%

seed_artists_names = [
    'Mastodon',
    'Gojira',
    'Jinjer',
    'Tool',
    'Lacuna Coil'
]

all_artists = collect_seed_artists(sp, seed_artists_names)
all_artists


# %%
