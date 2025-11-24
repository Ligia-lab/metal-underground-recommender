#%%

import sys
import os

# adiciona a pasta raiz do projeto ao PYTHONPATH
sys.path.append(os.path.abspath(".."))

from src.spotify_client import get_spotify_client

sp = get_spotify_client()
results = sp.search(q='Mastodon', type='artist', limit=1)
results['artists']['items'][0]['name'], results['artists']['items'][0]['id']


# %%
