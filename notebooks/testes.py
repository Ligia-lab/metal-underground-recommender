#%%

import os
import sys

sys.path.append(os.path.abspath(".."))

import pandas as pd
from src.spotify_client import get_spotify_client
from src.features import get_artist_by_name, collect_seed_artists
from src.dataset import build_basic_artists_df
from src.features import add_genre_vectors, get_genre_feature_matrix

#%%

sp = get_spotify_client()

#%%

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
    'Lacuna Coil',
    'Eths',
    'Alien Weaponry',
    'Behemoth',
    'Crypta',
    'Epica',
    'Ghost',
    'HIM',
    'Dir en Grey',
    'Septicflesh',
    'Siouxsie and the Banshees',
    'Sisters of Mercy',
    'VV',
    'Depeche Mode',
    'Joy Division',
    'London After Midnight'
]

#%%

all_artists = collect_seed_artists(sp, seed_artists_names)

#%%

len(all_artists)

# %%

df_artists = build_basic_artists_df(all_artists)
df_artists

# %%

df_artists.to_csv("../data/artists_basic.csv", index=False)

# %%

df_artists = pd.read_csv('../data/artists_basic.csv')

# %%

df_artists.head()

#%%

df_with_genres, mlb = add_genre_vectors(df_artists)
df_with_genres.head()

# %%

X, genre_cols = get_genre_feature_matrix(df_with_genres)
X.shape, len(genre_cols)

# %%

df_with_genres, mlb = add_genre_vectors(df_artists)
# %%

df_with_genres.columns

# %%

df = df_artists

print("RAW VALUES DA COLUNA 'genres':\n")
for i in range(5):
    print(f"{i}: {repr(df.loc[i, 'genres'])}")

# %%

