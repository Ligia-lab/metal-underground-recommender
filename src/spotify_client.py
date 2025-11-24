#%%
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#%%

load_dotenv()

# %%

# client_id = os.getenv('SPOTIFY_CLIENT_ID')
# client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# auth_manager = SpotifyClientCredentials(
#     client_id=client_id,
#     client_secret=client_secret
# )

# sp = spotipy.Spotify(auth_manager=auth_manager)

# query = 'Mastodon'
# result = sp.search(q=query, type='artist', limit=1)

# if result["artists"]["items"]:
#     artist = result["artists"]["items"][0]
#     print("Nome:", artist["name"])
#     print("ID:", artist["id"])
#     print("Popularidade:", artist["popularity"])
#     print("Gêneros:", artist["genres"])
# else:
#     print("Artista não encontrado.")

# %%

def get_spotify_client():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    return sp

# %%

