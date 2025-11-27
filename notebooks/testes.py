#%%
ROOT_PATH = os.path.abspath("..")   # um nível acima da pasta notebooks
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

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

from src.features import get_artist_vector, AUDIO_FEATURES

sp = get_spotify_client()
# %%
artist = get_artist_by_name(sp, "Metallica")
artist["name"], artist["id"]

# %%
artist_id = artist["id"]
vec = get_artist_vector(sp, artist_id)

print("Vetor:", vec)
print("Tipo :", type(vec))
print("Shape:", vec.shape if vec is not None else None)

# %%
dict(zip(AUDIO_FEATURES, vec))

# %%
# 1) pegar uma música qualquer
track_search = sp.search(q="Master of Puppets", type="track", limit=1)
track = track_search["tracks"]["items"][0]
track_id = track["id"]
track["name"], track_id

# %%
try:
    feats = sp.audio_features([track_id])
    print("Resultado:", feats)
except Exception as e:
    print("Erro:", e)

# %%
