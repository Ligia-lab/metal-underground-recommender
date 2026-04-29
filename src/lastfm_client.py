import os
from dotenv import load_dotenv
import requests

load_dotenv()

LASTFM_API_BASE = "https://ws.audioscrobbler.com/2.0/"


def get_lastfm_api_key() -> str:
    """
    Lê e retorna a API key da Last.fm a partir das variáveis de ambiente.
    A variável LASTFM_API_KEY deve estar definida no arquivo .env ou
    no ambiente do sistema.

    Retorno
    -------
    str
        API key da Last.fm.

    Raises
    ------
    ValueError
        Se a variável de ambiente não estiver definida.
    """
    api_key = os.getenv("LASTFM_API_KEY")
    if not api_key:
        raise ValueError(
            "LASTFM_API_KEY não encontrada. "
            "Defina-a no arquivo .env ou nas variáveis de ambiente."
        )
    return api_key


def lastfm_get(method: str, params: dict) -> dict:
    """
    Faz uma requisição GET autenticada à API da Last.fm.

    Adiciona automaticamente os parâmetros obrigatórios:
        - method
        - api_key
        - format=json

    Parâmetros
    ----------
    method : str
        Nome do método da API Last.fm (ex: 'artist.getInfo').
    params : dict
        Parâmetros adicionais da requisição (ex: {'artist': 'Gojira'}).

    Retorno
    -------
    dict
        JSON de resposta da API já convertido em dicionário Python.

    Raises
    ------
    requests.HTTPError
        Se a resposta HTTP indicar erro (status 4xx ou 5xx).
    """
    api_key = get_lastfm_api_key()

    payload = {
        "method": method,
        "api_key": api_key,
        "format": "json",
        **params,
    }

    response = requests.get(LASTFM_API_BASE, params=payload, timeout=10)
    response.raise_for_status()
    return response.json()