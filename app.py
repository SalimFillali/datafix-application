# Bibiliothèques de manipulation des données
import pandas as pd
import numpy as np

# Bibiliothèques de ML
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack, csr_matrix

# Import des données
path = ('data\df_film.csv')
data = pd.read_csv(path)

# =====================================================================
# ---------------------  Modèle de recommandation ---------------------
# =====================================================================
scaler = MinMaxScaler()
vectorizer = TfidfVectorizer()

# Features
X_genres = vectorizer.fit_transform(data['Genres'])
X_num_scaled = scaler.fit_transform(data[['Popularité','Note','Votes']])
X_num = csr_matrix(X_num_scaled)
X = hstack([X_genres, X_num])

# Model
model = NearestNeighbors(n_neighbors=6)
model.fit(X)
distance, indices = model.kneighbors(X)

# =====================================================================
# ---------------------  Fonction d'appel -----------------------------
# =====================================================================

def reco_film(titre:str):
    film = data[data['Titre'] == titre]
    indice_film = film.index[0]
    reco_indices = indices[indice_film,]
    film_reco = data.iloc[reco_indices[1:6],]
    return film_reco
