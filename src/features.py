#%%

import spotipy
import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import ast

#%%

def get_artist_by_name(sp, name):
    """
    Busca um artista pelo nome usando a API do Spotify.

    Parâmetros
    ----------
    sp : spotipy.Spotify
        Cliente autenticado da API do Spotify.
    name : str
        Nome do artista a ser buscado.

    Retorno
    -------
    dict ou None
        Retorna o primeiro artista encontrado (como um dicionário com dados do Spotify)
        ou None caso nenhum artista corresponda ao nome informado.

    O que essa função faz?
    -----------------------
    - Envia uma requisição de busca `search` para o Spotify, filtrando pelo tipo "artist".
    - Limita o resultado ao primeiro item mais relevante (`limit=1`).
    - Se encontrar artistas, retorna o primeiro do ranking.
    - Se não encontrar nada, retorna `None`.

    Exemplo:
    >>> get_artist_by_name(sp, "Gojira")
    { ... dados do artista ... }
    """
    res = sp.search(q=name, type="artist", limit=1)
    items = res["artists"]["items"]
    return items[0] if items else None

# %%

def collect_seed_artists(sp, seed_artists_names):
    """
    Busca múltiplos artistas iniciais ("seed artists") no Spotify e retorna
    um dicionário com informações padronizadas de cada um.

    Parâmetros
    ----------
    sp : spotipy.Spotify
        Cliente autenticado da API do Spotify.

    seed_artists_names : list[str]
        Lista de nomes de artistas que o usuário quer usar como ponto de partida
        no sistema de recomendação.

    Retorno
    -------
    dict
        Um dicionário onde cada chave é o `artist_id` e o valor é outro dicionário
        contendo informações essenciais sobre o artista:
            {
                'id': str,
                'name': str,
                'popularity': int,
                'genres': list[str],
                'spotify_url': str
            }

    O que essa função faz?
    -----------------------
    - Itera sobre todos os nomes de artistas fornecidos pelo usuário.
    - Para cada nome:
        * Realiza uma busca no Spotify usando o endpoint `search(type='artist')`.
        * Trata erros da API (como falhas temporárias, rate limits, tokens inválidos).
        * Caso encontre o artista, coleta:
              - ID
              - Nome
              - Popularidade
              - Lista de gêneros
              - URL oficial do Spotify
        * Evita duplicatas usando `artist_id` como chave.
    - Retorna um dicionário consolidado contendo todos os artistas encontrados.

    Logs impressos:
    ---------------
    - Cada artista sendo buscado.
    - Caso nenhum resultado seja encontrado.
    - Caso o artista já tenha aparecido na lista.
    - Informações resumidas de cada artista encontrado.
    - Número total de artistas seed coletados ao final.

    Exemplo de uso:
    ---------------
    >>> seeds = ["Gojira", "Meshuggah", "Jinjer"]
    >>> artists = collect_seed_artists(sp, seeds)
    >>> len(artists)
    3

    """    
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

BASE_COLS = ['id', 'name', 'popularity', 'genres', 'spotify_url']

#%%

def _normalize_genres(value):
    """
    Normaliza o conteúdo da coluna 'genres' para garantir que sempre seja retornada
    uma lista de strings. Essa função é essencial para padronizar os dados antes
    de aplicar técnicas como One-Hot Encoding ou MultiLabelBinarizer.

    Por que essa função existe?
    ---------------------------
    Durante o processo de coleta e armazenamento (especialmente ao salvar como CSV),
    a coluna `genres` pode assumir diferentes formatos:

    Exemplos de formatos de entrada tratados:
    -----------------------------------------
    1) Lista real (vinda diretamente da API):
         ['progressive metal', 'sludge metal']

    2) String representando lista Python (caso deste projeto):
         "['progressive metal', 'sludge metal', 'stoner metal']"

    3) String com colchetes, mas sem aspas:
         "[progressive metal, sludge metal]"

    4) String simples separada por vírgulas:
         "progressive metal, sludge metal, stoner metal"

    5) Valor vazio, NaN ou string vazia:
         ""
         "nan"
         None
         NaN

    O objetivo é transformar todos esses formatos em:
         ['progressive metal', 'sludge metal', 'stoner metal']

    Parâmetros
    ----------
    value : qualquer tipo
        Um valor da coluna `genres` do DataFrame. Pode ser lista, string,
        NaN ou valores inesperados.

    Retorno
    -------
    list[str]
        Lista de gêneros normalizados. Caso o valor não possa ser interpretado,
        retorna uma lista vazia.

    Funcionamento interno
    ----------------------
    - Se já for uma lista → garante que todos os elementos são strings limpas.
    - Se for NaN → retorna lista vazia.
    - Se for string:
        1) Tenta interpretar como lista Python usando `ast.literal_eval`.
           Isso resolve o caso mais comum:
              "['metal', 'djent']"
        2) Se falhar, remove colchetes e faz split por vírgula.
    - Se nada servir → retorna [].

    Exemplo:
    --------
    >>> _normalize_genres("['metal', 'djent']")
    ['metal', 'djent']

    >>> _normalize_genres("[metal, djent]")
    ['metal', 'djent']

    >>> _normalize_genres("metal, djent")
    ['metal', 'djent']

    >>> _normalize_genres(None)
    []

    """

    if isinstance(value, list):
        return value
    
    if pd.isna(value):
        return []
    
    if isinstance(value, str):
        text = value.strip()
        if text == "" or text.lower() == "nan":
            return []
        
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                # garantir que tudo é str e sem espaços extras
                return [str(x).strip() for x in parsed]
        except Exception:
            pass
        
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1].strip()
        
        parts = [s.strip() for s in text.split(",") if s.strip()]

        return parts
        
    return []

# %%

def add_genre_vectors(df_artists: pd.DataFrame):
    """
    Converte a coluna 'genres' do DataFrame em vetores numéricos usando
    MultiLabelBinarizer, criando uma coluna binária para cada gênero encontrado.
    Retorna um novo DataFrame contendo essas colunas adicionais.

    Objetivo da função
    -------------------
    Transformar uma coluna com listas de gêneros musicais em uma representação
    vetorial (one-hot encoding multi-label). Isso é essencial para permitir:

    - Cálculo de similaridade entre artistas (ex.: cosine similarity)
    - Construção de sistemas de recomendação baseados em gênero
    - Treinamento de modelos que exigem entrada numérica

    O que esta função faz?
    -----------------------
    1) Cria uma cópia do DataFrame original para evitar mutações.
    2) Normaliza a coluna `genres` usando `_normalize_genres`, garantindo que cada
       valor seja sempre uma lista de strings.
    3) Aplica `MultiLabelBinarizer` para transformar as listas em uma matriz 0/1.
       - Cada gênero vira uma coluna nova.
       - Cada linha ganha 1 se o artista possui aquele gênero, ou 0 caso contrário.
    4) Concatena o DataFrame original com as novas colunas de gênero.
    5) Retorna:
         - O novo DataFrame com colunas extras
         - O objeto `MultiLabelBinarizer`, útil para interpretar as classes depois

    Parâmetros
    ----------
    df_artists : pandas.DataFrame
        DataFrame contendo pelo menos a coluna 'genres'. A coluna pode conter listas
        reais ou strings representando listas (como no CSV).

    Retorno
    -------
    tuple
        df_with_genres : pandas.DataFrame
            O DataFrame original acrescido de colunas binárias para cada gênero.
        mlb : MultiLabelBinarizer
            O codificador treinado, contendo os nomes de todas as classes (gêneros).

    Exemplo de funcionamento
    ------------------------
    Entrada:
        genres
        -------------------------
        ['prog metal', 'djent']
        ['death metal']
        ['prog metal', 'sludge metal']

    Saída (colunas novas):
        prog metal | djent | death metal | sludge metal
        ------------------------------------------------
            1      |   1   |      0      |      0
            0      |   0   |      1      |      0
            1      |   0   |      0      |      1

    Mensagens de debug:
    -------------------
    - Mostra exemplos de gêneros normalizados.
    - Exibe quantos gêneros distintos foram encontrados.
    - Lista alguns dos gêneros detectados.

    Observações
    -----------
    Esta função não altera o DataFrame original. Sempre retorna uma nova cópia
    com as colunas expandidas.

    """
    df = df_artists.copy()
    df['genres'] = df['genres'].apply(_normalize_genres) 

    print("Exemplos de genres normalizados:")
    print(df["genres"].head())

    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(df['genres'])

    print(f"\nTotal de gêneros distintos encontrados: {len(mlb.classes_)}")
    if len(mlb.classes_) > 0:
        print("Alguns gêneros:", mlb.classes_[:10])

    genre_df = pd.DataFrame(
        genre_matrix,
        columns=mlb.classes_,
        index=df.index
    )

    df_with_genres = pd.concat([df, genre_df], axis=1)

    return df_with_genres, mlb

# %%

def get_genre_feature_matrix(df_with_genres: pd.DataFrame):
    """
    Extrai do DataFrame as colunas correspondentes aos gêneros musicais e retorna
    a matriz numérica de features juntamente com a lista de nomes das colunas.

    Objetivo da função
    -------------------
    Esta função isola somente as colunas binárias geradas pela etapa de 
    one-hot encoding de gêneros (via MultiLabelBinarizer em `add_genre_vectors`).
    O resultado é uma matriz adequada para cálculos de similaridade, clustering
    ou entrada em modelos de machine learning.

    O que esta função faz?
    -----------------------
    1) Identifica todas as colunas que NÃO fazem parte das colunas base
       (id, name, popularity, genres, spotify_url).  
       Essas colunas extras são justamente os gêneros musicais.
    2) Extrai seus valores em formato matricial (`numpy.ndarray`).
    3) Retorna:
        - A matriz X (shape: número de artistas × número de gêneros)
        - A lista de colunas de gênero (útil para interpretação e debug)

    Parâmetros
    ----------
    df_with_genres : pandas.DataFrame
        DataFrame retornado por `add_genre_vectors`, contendo colunas binárias
        para cada gênero musical.

    Retorno
    -------
    tuple
        X : numpy.ndarray
            Matriz contendo apenas os valores numéricos (0/1) referentes aos gêneros.
        genre_cols : list[str]
            Lista de nomes das colunas de gênero utilizadas na matriz X.

    Exemplo
    -------
    Supondo que df_with_genres tenha estas colunas:

        ['id', 'name', 'popularity', 'genres', 'spotify_url',
         'death metal', 'groove metal', 'prog metal']

    A função irá retornar:

        X = matriz Nx3 com 0s e 1s
        genre_cols = ['death metal', 'groove metal', 'prog metal']

    """
    genre_cols = [c for c in df_with_genres.columns if c not in BASE_COLS]
    X = df_with_genres[genre_cols].values
    return X, genre_cols

# %%
