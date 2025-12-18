# 🤘 Metal Underground Recommender

Metal Underground Recommender is a recommendation system for lesser-known (underground) metal bands, built exclusively using public data from the Spotify API, while respecting the current limitations of the API (deprecated or restricted endpoints).

The user provides bands they already like, and the system searches for new, similar artists based on musical genres, prioritizing bands with low or no popularity.

---

## 🧠 Project Idea

Spotify has deprecated or restricted some classic endpoints, such as:

- artist_related_artists  
- audio_features  

Because of this, the project adopts a 100% viable and up-to-date approach, based on:

- Artist search via search  
- Extraction and analysis of musical genres  
- Artist similarity using genre-based vectors  
- Explicit popularity control to focus on underground bands  

The goal is to generate real and dynamic recommendations without relying on external datasets or obsolete endpoints.

---

## ⚙️ How the System Works

### 1️⃣ User Input

The user provides a list of bands they like, for example:

Mastodon, Gojira, Jinjer

---

### 2️⃣ Artist Collection via the Spotify API

For each band provided:

- The system searches for the artist by name using search  
- Collects the artist’s musical genres  
- For each genre found, performs new searches for artists within that genre  

This creates a dynamic pool of candidate artists, based exclusively on compatible genres.

---

### 3️⃣ Dataset Construction

For each collected artist, the system stores:

- id  
- name  
- popularity  
- genres  
- spotify_url  

These data are organized into a pandas DataFrame.

---

### 4️⃣ Genre Vectorization

- The genres column is normalized  
- Each genre becomes a binary column (one-hot encoding)  
- The result is a genre matrix per artist  

This matrix is the basis for similarity calculations.

---

### 5️⃣ User Profile

- The user profile is computed as the average of the genre vectors of the bands provided  
- This vector represents the user’s musical preferences  

---

### 6️⃣ Recommendation

For each candidate artist:

- Cosine similarity is calculated against the user profile  
- An underground factor (inverse popularity) is applied  
- Strict filters are enforced:  
  - ❌artists without genres  
  - ❌artists with zero similarity  
  - ❌artists above a configurable popularity threshold (for example, greater than 50)  

The final result is a ranked list of similar and lesser-known bands.

---

## 🚀 Features

- Dynamic artist search via the Spotify API  
- Genre-based expansion only (no deprecated endpoints)  
- Content-based recommendation system  
- Maximum popularity control  
- Interactive Streamlit interface  
- Modular and fully documented code  

---

## 📁 Project Structure
```
metal-underground-recommender  
├── src  
│   ├── spotify_client.py      Spotify API authentication  
│   ├── dataset.py             Artist collection and genre-based expansion  
│   ├── features.py            Genre normalization and vectorization  
│   └── recommender.py         Recommendation logic  
├── notebooks                  Tests and exploratory analysis  
├── app_streamlit.py           Interactive Streamlit app  
├── requirements.txt           Project dependencies  
├── .env.example               Environment variables example  
└── README.md  
```
---

## 🛠️ Installation

1. Clone the repository  
```
git clone https://github.com/Ligia-lab/metal-underground-recommender.git  
cd metal-underground-recommender  
```
2. Create a virtual environment  
```
python -m venv .venv  
source .venv/bin/activate  
```
3. Install dependencies  
```
pip install -r requirements.txt  
```
4. Configure environment variables  

Create a .env file with:
```
SPOTIFY_CLIENT_ID=your_client_id  
SPOTIFY_CLIENT_SECRET=your_client_secret  
```
---

## 🌐 Running the App (Streamlit)
```
streamlit run app_streamlit.py  
```
In the app you can:

- Enter bands you like  
- Adjust the number of recommendations  
- Adjust the underground factor weight  
- Define the maximum allowed popularity  
- View recommendations in a table  

---

## 🧪 Usage via Code

The functions can also be used directly in code or notebooks:
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

## ⚠️ Known Limitations

- The Spotify API does not allow access to the full artist catalog  
- There is no endpoint to retrieve all Spotify artists  
- The project relies on controlled genre-based expansion  
- Endpoints such as related artists and audio features are not used  

These limitations are explicitly handled in the system design.

---

## 🎯 Project Goal

This project was created with a focus on:

- Technical portfolio development  
- Applied data engineering  
- Content-based recommendation systems  
- Conscious and realistic use of real-world APIs  

---

## 🚀 Next Steps of the Project

The next steps of the **Metal Underground Recommender** are defined based on the current state of the repository and on technically feasible evolutions.

### 1️⃣ Streamlit App Consolidation
Improve interface for user interaction:

- Clickable links to artists on Spotify

### 2️⃣ Local Cache to Avoid Repeated API Calls
Implement local persistence of processed data to improve performance:

- Cache using `pickle`, `Parquet`, or SQLite
- Significant reduction in Spotify API calls
- Faster and more stable application execution

### 3️⃣ FastAPI API Creation
Expose the recommender as an independent service:

- Endpoint that receives:
  
      {
        "likes": ["Gojira", "Mastodon"]
      }

- Structured response with recommended artists, similarity, and popularity
- Ability to reuse the recommender core outside Streamlit

### 4️⃣ Similarity Calculation Improvements
Refine the current recommendation logic:

- Use of TF-IDF for genre vectorization
- Configurable minimum similarity threshold
- Genre-based weighting to improve recommendation relevance

### 5️⃣ Project Presentation Notebook
Create an explanatory and visual notebook for documentation and portfolio purposes:

- Overview of the complete workflow
- Charts and exploratory analyses
- Genre distribution analysis
- Detailed explanation of the recommender logic

---


## 📜 License

This project is intended for educational and demonstrative purposes.
