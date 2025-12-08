#%%

import pandas as pd

# %%

def build_basic_artists_df(all_artists: dict):
    records = []

    for artist_id, info in all_artists.items():
        records.append({
            'id': info['id'],
            'name': info['name'],
            'popularity': info['popularity'],
            'genres': info['genres'],
            'spotify_url': info['spotify_url']
        })

    df = pd.DataFrame(records)
    return df

# %%
