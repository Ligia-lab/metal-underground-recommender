#%%

import spotipy

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
