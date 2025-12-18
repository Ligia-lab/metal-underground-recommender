# 🤘 Metal Underground Recommender

O Metal Underground Recommender é um sistema de recomendação de bandas de metal menos conhecidas (underground), construído exclusivamente com dados públicos da API do Spotify, respeitando as limitações atuais da API (endpoints obsoletos ou restritos).

O usuário informa bandas que já gosta, e o sistema busca novos artistas semelhantes a partir dos gêneros musicais, priorizando bandas com baixa ou nenhuma popularidade.

---

## 🧠 Ideia do Projeto

O Spotify deixou de disponibilizar ou restringiu alguns endpoints clássicos, como:

- artist_related_artists  
- audio_features  

Por isso, este projeto adota uma abordagem 100% viável e atual, baseada em:

- Busca de artistas via search  
- Extração e análise de gêneros musicais  
- Similaridade entre artistas usando vetores de gêneros  
- Controle explícito de popularidade para focar em bandas underground  

O objetivo é criar recomendações reais e dinâmicas sem depender de datasets externos ou endpoints obsoletos.

---

## ⚙️ Como o Sistema Funciona

### 1️⃣ Entrada do Usuário

O usuário informa uma lista de bandas que gosta, por exemplo:

Mastodon, Gojira, Jinjer

---

### 2️⃣ Coleta de Artistas na API do Spotify

Para cada banda informada:

- O sistema busca o artista pelo nome usando search  
- Coleta seus gêneros musicais  
- Para cada gênero encontrado, realiza novas buscas por artistas daquele gênero  

Isso cria um universo dinâmico de artistas candidatos, baseado exclusivamente em gêneros compatíveis.

---

### 3️⃣ Construção do Dataset

Para cada artista coletado, o sistema armazena:

- id  
- name  
- popularity  
- genres  
- spotify_url  

Esses dados são organizados em um DataFrame pandas.

---

### 4️⃣ Vetorização de Gêneros

- A coluna genres é normalizada  
- Cada gênero vira uma coluna binária (one-hot encoding)  
- O resultado é uma matriz de gêneros por artista  

Essa matriz é a base para o cálculo de similaridade.

---

### 5️⃣ Perfil do Usuário

- O perfil do usuário é calculado como a média dos vetores de gêneros das bandas informadas  
- Esse vetor representa os gostos musicais do usuário  

---

### 6️⃣ Recomendação

Para cada artista candidato:

- Calcula-se a similaridade de cosseno com o perfil do usuário  
- Aplica-se um fator de underground (popularidade inversa)  
- São aplicados filtros rígidos:  
  - ❌artistas sem gêneros  
  - ❌artistas com similaridade igual a zero  
  - ❌artistas com popularidade acima de um limite configurável (exemplo: maior que 50)  

O resultado final é um ranking de bandas similares e menos conhecidas.

---

## 🚀 Funcionalidades

- Busca dinâmica via API do Spotify  
- Expansão baseada apenas em gêneros (sem endpoints obsoletos)  
- Sistema de recomendação content-based  
- Controle de popularidade máxima  
- Interface interativa com Streamlit  
- Código modular e totalmente documentado  

---

## 📁 Estrutura do Projeto

```
metal-underground-recommender  
├── src  
│   ├── spotify_client.py      Autenticação com a API do Spotify  
│   ├── dataset.py             Coleta e expansão de artistas por gênero  
│   ├── features.py            Normalização e vetorização de gêneros  
│   └── recommender.py         Lógica de recomendação  
├── notebooks                  Testes e análises exploratórias  
├── app_streamlit.py           App interativo em Streamlit  
├── requirements.txt           Dependências do projeto  
├── .env.example               Exemplo de variáveis de ambiente  
└── README.md  
```
---

## 🛠️ Instalação

1. Clonar o repositório
```
git clone https://github.com/Ligia-lab/metal-underground-recommender.git  
cd metal-underground-recommender  
```
2. Criar ambiente virtual  
```
python -m venv .venv  
source .venv/bin/activate  
```
3. Instalar dependências  
```
pip install -r requirements.txt  
```
4. Configurar variáveis de ambiente  

Criar um arquivo .env com:
```
SPOTIFY_CLIENT_ID=seu_client_id  
SPOTIFY_CLIENT_SECRET=seu_client_secret  
```
---

## 🌐 Rodando o App (Streamlit)
```
streamlit run app_streamlit.py  
```
No app é possível:

- Informar bandas que você gosta  
- Ajustar quantidade de recomendações  
- Ajustar peso do fator underground  
- Definir popularidade máxima permitida  
- Visualizar as recomendações em tabela  

---

## 🧪 Uso via Código

As funções também podem ser usadas diretamente em código ou notebook:
```
sp = get_spotify_client()  

df_with_genres = expand_artists_from_user_likes(  
    sp,  
    user_likes=["Gojira", "Meshuggah"]  
)  

recs = recommend_artists_by_genre(  
    df_with_genres,  
    user_likes=["Gojira", "Meshuggah"]  
)  
```
---

## ⚠️ Limitações Conhecidas

- A API do Spotify não permite acesso completo a todos os artistas  
- Não existe endpoint para listar todo o catálogo do Spotify  
- O projeto trabalha com expansão controlada por gênero  
- Endpoints como related artists e audio features não são utilizados  

Essas limitações são tratadas explicitamente no design do sistema.

---



## 🎯 Objetivo do Projeto

Este projeto foi criado com foco em:

- Portfólio técnico  
- Engenharia de dados aplicada  
- Sistemas de recomendação content-based  
- Uso consciente de APIs reais e suas restrições  

---

## 🚀 Próximas Etapas do Projeto

As próximas etapas do **Metal Underground Recommender** foram definidas com base no estado atual do repositório e em evoluções tecnicamente viáveis.

### 1️⃣ Consolidação do app em Streamlit
Melhorar a interface para interação do usuário:

- Links clicáveis para os artistas no Spotify

### 2️⃣ Cache local para evitar chamadas repetidas à API
Implementar persistência local dos dados processados para melhorar performance:

- Cache utilizando `pickle`, `Parquet` ou SQLite
- Redução significativa de chamadas à Spotify API
- Execução mais rápida e estável da aplicação

### 3️⃣ Criação de uma API com FastAPI
Expor o recomendador como um serviço independente:

- Endpoint que recebe:
  
      {
        "likes": ["Gojira", "Mastodon"]
      }

- Retorno estruturado com artistas recomendados, similaridade e popularidade
- Possibilidade de reutilizar o core do recomendador fora do Streamlit

### 4️⃣ Melhoria do cálculo de similaridade
Refinar a lógica atual de recomendação:

- Uso de TF-IDF para vetorização de gêneros
- Threshold mínimo de similaridade configurável
- Ajuste de peso por gênero para melhorar relevância das recomendações

### 5️⃣ Notebook de apresentação do projeto
Criar um notebook explicativo e visual para documentação e portfólio:

- Visão geral do workflow do projeto
- Gráficos e análises exploratórias
- Distribuição de gêneros
- Explicação detalhada da lógica do recomendador

---

## 📜 Licença

Projeto com fins educacionais e demonstrativos.



