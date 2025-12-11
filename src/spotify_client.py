#%%
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#%%

load_dotenv()

# %%

def get_spotify_client():
    """
    Cria e retorna um cliente autenticado da API do Spotify utilizando o fluxo
    Client Credentials (Client ID + Client Secret).

    Objetivo da função
    -------------------
    Centralizar a lógica de autenticação com o Spotify usando variáveis de
    ambiente, garantindo que qualquer parte do projeto possa obter um cliente
    `spotipy.Spotify` já autenticado e pronto para fazer chamadas à API.

    O que esta função faz?
    -----------------------
    1) Lê as variáveis de ambiente:
         - SPOTIFY_CLIENT_ID
         - SPOTIFY_CLIENT_SECRET

       Essas variáveis devem estar definidas em um arquivo `.env` ou configuradas
       manualmente no ambiente.

    2) Cria um objeto `SpotifyClientCredentials`, responsável por gerar o token
       de acesso via fluxo Client Credentials.

    3) Cria um cliente Spotipy:
         sp = spotipy.Spotify(auth_manager=auth_manager)

    4) Retorna o cliente pronto para:
         - buscar artistas
         - consultar tracks
         - consultar álbuns
         - acessar endpoints públicos do Spotify

    """
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    return sp

# %%

