"""Page Recommandation - DATAFIX.

Moteur de recommandation basé sur le notebook ML :
  - TF-IDF sur les Genres
  - MinMaxScaler sur (Popularité, Note, Votes)
  - NearestNeighbors (k=6) avec hstack
Enrichissement live via l'API TMDB (synopsis, trailers).
"""

from pathlib import Path
import re
import urllib.parse

import numpy as np
import pandas as pd
import requests
import streamlit as st

from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler


# =====================================================================
# Configuration de page & chemins
# =====================================================================
st.set_page_config(
    page_title="DATAFIX – Recommandation",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "df_film.csv"
LOGO = BASE_DIR / "asset" / "logo.png"

# Token TMDB (issu du notebook APi Movies vidéos.ipynb).
# Idéalement à déplacer dans .streamlit/secrets.toml en production.
TMDB_BEARER = (
    "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5Y2IwZTY2ZDU4M2NlMjRlNzhkMWIyNzc2YmUxYTJiMCIs"
    "Im5iZiI6MTc3NzI5NjYzNS4wODksInN1YiI6IjY5ZWY2NGZiYTQ5YzYxY2QwNzE1MWFiNiIsInNj"
    "b3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.kcNXcdjcIvWsz84XKCFBrOopCYfR7g4yg-IMIV2YYbU"
)
TMDB_HEADERS = {"accept": "application/json", "Authorization": f"Bearer {TMDB_BEARER}"}


# =====================================================================
# Styles (charte DATAFIX : noir + or #F5C518)
# =====================================================================
st.markdown(
    """
<style>
/* ---------- Hero / titres ---------- */
.reco-hero {
    text-align: center;
    padding: 1rem 0 0.4rem 0;
}
.reco-hero h1 {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin: 0;
}
.reco-hero .sub {
    color: #9A9AA0;
    font-size: 1.05rem;
    margin-top: 0.4rem;
}
.gold-line {
    width: 84px;
    height: 4px;
    background: #F5C518;
    border-radius: 4px;
    margin: 0.8rem auto 1.4rem auto;
}

/* ---------- Section "film sélectionné" ---------- */
.selected-card {
    padding: 1.6rem;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(245,197,24,0.08), rgba(255,255,255,0.03));
    border: 1px solid rgba(245,197,24,0.20);
    box-shadow: 0 10px 35px rgba(0,0,0,0.35);
    margin-bottom: 0.6rem;
}
.selected-title {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 0.3rem;
}
.selected-meta {
    color: #B8B8B8;
    font-size: 0.98rem;
    margin-bottom: 1rem;
}
.chip {
    display: inline-block;
    padding: 4px 12px;
    margin: 2px 4px 2px 0;
    border-radius: 999px;
    background: rgba(245,197,24,0.10);
    border: 1px solid rgba(245,197,24,0.35);
    color: #F5C518;
    font-size: 0.82rem;
    font-weight: 600;
}
.note-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #F5C518;
    color: #0E0E10;
    font-weight: 800;
    padding: 6px 12px;
    border-radius: 10px;
    font-size: 0.95rem;
}
.synopsis {
    color: #D6D6D6;
    line-height: 1.65;
    font-size: 1rem;
    margin-top: 0.6rem;
}

/* ---------- Grille recommandations ---------- */
.section-title {
    font-size: 1.3rem;
    font-weight: 800;
    margin: 1.8rem 0 0.6rem 0;
    padding-left: 12px;
    border-left: 4px solid #F5C518;
}
.reco-card {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    transition: transform .28s ease, box-shadow .28s ease, border-color .28s ease;
    height: 100%;
}
.reco-card:hover {
    transform: translateY(-6px);
    border-color: rgba(245,197,24,0.55);
    box-shadow: 0 18px 40px rgba(0,0,0,0.55), 0 0 0 1px rgba(245,197,24,0.2);
}
.poster-wrap {
    position: relative;
    aspect-ratio: 2 / 3;
    background: #111;
    overflow: hidden;
}
.poster-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform .6s ease;
}
.reco-card:hover .poster-wrap img { transform: scale(1.06); }
.poster-rank {
    position: absolute;
    top: 10px;
    left: 10px;
    background: rgba(0,0,0,0.75);
    color: #F5C518;
    font-weight: 800;
    font-size: 0.8rem;
    padding: 3px 9px;
    border-radius: 999px;
    border: 1px solid rgba(245,197,24,0.4);
}
.poster-note {
    position: absolute;
    top: 10px;
    right: 10px;
    background: #F5C518;
    color: #0E0E10;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 8px;
    font-size: 0.82rem;
}
.card-body {
    padding: 0.9rem 1rem 1.05rem 1rem;
}
.card-title {
    font-size: 1.02rem;
    font-weight: 700;
    line-height: 1.25;
    margin-bottom: 0.25rem;
    /* clamp 2 lignes */
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    min-height: 2.55rem;
}
.card-sub {
    color: #9A9AA0;
    font-size: 0.82rem;
    margin-bottom: 0.55rem;
}
.fun-fact {
    background: rgba(245,197,24,0.07);
    border-left: 3px solid #F5C518;
    color: #E8E8E8;
    font-size: 0.83rem;
    line-height: 1.45;
    padding: 8px 10px;
    border-radius: 6px;
    margin-bottom: 0.65rem;
    min-height: 3.3rem;
}
.fun-fact b { color: #F5C518; }
.trailer-btn {
    display: block;
    text-align: center;
    text-decoration: none;
    background: transparent;
    color: #F5C518;
    border: 1px solid rgba(245,197,24,0.55);
    padding: 7px 10px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.85rem;
    transition: background .2s ease, color .2s ease;
}
.trailer-btn:hover {
    background: #F5C518;
    color: #0E0E10;
}
.trailer-btn.disabled {
    color: #555;
    border-color: rgba(255,255,255,0.10);
    pointer-events: none;
}

/* ---------- Petites métriques sous l'image principale ---------- */
.mini-metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-top: 0.9rem;
}
.metric-tile {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 10px 8px;
    text-align: center;
}
.metric-tile .v {
    font-weight: 800;
    font-size: 1rem;
    color: #F5C518;
}
.metric-tile .l {
    color: #9A9AA0;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 2px;
}

/* Légères animations d'entrée */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.reco-card, .selected-card { animation: fadeUp .45s ease both; }
</style>
""",
    unsafe_allow_html=True,
)


# =====================================================================
# Sidebar
# =====================================================================
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)
    st.caption("v0.2 · Sprint 4 · 2026")
    st.markdown("---")
    st.markdown("**Moteur ML**")
    st.caption(
        "TF-IDF (Genres) + MinMaxScaler (Popularité, Note, Votes) "
        "→ NearestNeighbors (k=6)."
    )


# =====================================================================
# Chargement des données + entraînement du modèle (cache lourd)
# =====================================================================
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    # Nettoyage : on retire les doublons éventuels pour avoir un index stable
    df = df.drop_duplicates(subset=["Titre"], keep="first").reset_index(drop=True)
    return df


@st.cache_resource(show_spinner=False)
def fit_model(df: pd.DataFrame):
    scaler = MinMaxScaler()
    vectorizer = TfidfVectorizer()

    X_genres = vectorizer.fit_transform(df["Genres"].fillna(""))
    X_num_scaled = scaler.fit_transform(df[["Popularité", "Note", "Votes"]].fillna(0))
    X_num = csr_matrix(X_num_scaled)
    X = hstack([X_genres, X_num])

    model = NearestNeighbors(n_neighbors=6, metric="cosine")
    model.fit(X)
    distances, indices = model.kneighbors(X)
    return indices, distances


def reco_film(titre: str, df: pd.DataFrame, indices: np.ndarray) -> pd.DataFrame:
    """Retourne les 5 voisins les plus proches d'un film (hors lui-même)."""
    film = df[df["Titre"] == titre]
    if film.empty:
        return df.iloc[0:0]
    indice_film = film.index[0]
    reco_indices = indices[indice_film]
    return df.iloc[reco_indices[1:6]]


# =====================================================================
# Helpers
# =====================================================================
def yt_id(url: str | float | None) -> str | None:
    """Extrait l'ID YouTube d'une URL."""
    if not isinstance(url, str) or not url:
        return None
    m = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{6,})", url)
    return m.group(1) if m else None


def fmt_money(x: float) -> str:
    """Formatage compact d'un montant en €."""
    if not x or pd.isna(x) or x <= 0:
        return "—"
    if x >= 1_000_000:
        return f"{x/1_000_000:.1f} M€"
    if x >= 1_000:
        return f"{x/1_000:.0f} K€"
    return f"{int(x)} €"


def fmt_int(x: float) -> str:
    if pd.isna(x) or x is None:
        return "—"
    return f"{int(x):,}".replace(",", " ")


def duration_pretty(minutes: float) -> str:
    if not minutes or pd.isna(minutes) or minutes <= 0:
        return "—"
    h, m = divmod(int(minutes), 60)
    return f"{h}h{m:02d}" if h else f"{m} min"


def fun_fact(row: pd.Series) -> str:
    """Génère une petite info ludique qui intègre malin Budget/Votes/Recette/Durée."""
    budget = float(row.get("Budget") or 0)
    recette = float(row.get("Recette") or 0)
    votes = float(row.get("Votes") or 0)
    duree = float(row.get("Durée") or 0)
    annee = int(row.get("Année") or 0)
    note = float(row.get("Note") or 0)

    facts: list[str] = []

    # ROI au box-office
    if budget > 0 and recette > 0:
        roi = recette / budget
        if roi >= 5:
            facts.append(f"Carton au box-office : <b>×{roi:.1f}</b> sa mise")
        elif roi >= 1.5:
            facts.append(f"Rentabilité solide : <b>×{roi:.1f}</b> le budget")
        else:
            facts.append(f"Budget couvert à <b>{roi*100:.0f}%</b> au cinéma")
    elif budget > 0:
        if budget < 1_000_000:
            facts.append(f"Pépite à petit budget : <b>{fmt_money(budget)}</b>")
        elif budget >= 20_000_000:
            facts.append(f"Grosse production : <b>{fmt_money(budget)}</b>")
        else:
            facts.append(f"Budget maîtrisé : <b>{fmt_money(budget)}</b>")

    # Votes / popularité
    if votes >= 5000:
        facts.append(f"<b>{fmt_int(votes)}</b> spectateurs ont voté")
    elif votes >= 500:
        facts.append(f"Plébiscité par <b>{fmt_int(votes)}</b> votants")
    elif 1 <= votes < 50:
        facts.append(f"Pépite confidentielle (<b>{fmt_int(votes)}</b> votes)")

    # Durée
    if duree:
        if duree <= 90:
            facts.append(f"Format court : <b>{duration_pretty(duree)}</b>, idéal en semaine")
        elif duree >= 130:
            facts.append(f"Soirée longue : <b>{duration_pretty(duree)}</b> de cinéma")

    # Année
    if annee:
        if annee < 1990:
            facts.append(f"Un classique de <b>{annee}</b>")
        elif annee >= 2020:
            facts.append(f"Tout frais : sorti en <b>{annee}</b>")

    # Note élevée
    if note >= 7.8:
        facts.append(f"Très bien noté : <b>{note:.1f}/10</b>")

    return facts[0] if facts else "Un choix qui colle à vos goûts."


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def tmdb_details(tmdb_id: int) -> dict:
    """Récupère synopsis FR + vidéos du film via l'API TMDB."""
    out = {"overview": None, "trailer_key": None, "tagline": None}
    if not tmdb_id or pd.isna(tmdb_id):
        return out
    try:
        # Détails (synopsis + tagline)
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}?language=fr-FR",
            headers=TMDB_HEADERS,
            timeout=5,
        )
        if r.ok:
            j = r.json()
            out["overview"] = (j.get("overview") or "").strip() or None
            out["tagline"] = (j.get("tagline") or "").strip() or None

        # Vidéos (priorité FR -> EN)
        for lang in ("fr-FR", "en-US"):
            rv = requests.get(
                f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}/videos?language={lang}",
                headers=TMDB_HEADERS,
                timeout=5,
            )
            if not rv.ok:
                continue
            results = rv.json().get("results", [])
            yt = [
                v for v in results
                if v.get("site") == "YouTube"
                and v.get("type") in ("Trailer", "Teaser")
            ]
            if yt:
                # Préférer un Trailer "officiel"
                yt.sort(
                    key=lambda v: (v.get("type") != "Trailer", not v.get("official", False))
                )
                out["trailer_key"] = yt[0].get("key")
                break
    except requests.RequestException:
        pass
    return out


def best_youtube_key(row: pd.Series) -> str | None:
    """ID YouTube depuis le dataset, sinon depuis l'API TMDB."""
    k = yt_id(row.get("youtube_url"))
    if k:
        return k
    api = tmdb_details(row.get("id_tmdb_x"))
    return api.get("trailer_key")


def best_overview(row: pd.Series) -> str | None:
    """Synopsis FR via TMDB (avec cache)."""
    api = tmdb_details(row.get("id_tmdb_x"))
    return api.get("overview")


# =====================================================================
# Chargement + entraînement
# =====================================================================
with st.spinner("Préparation du moteur de recommandation…"):
    df = load_data()
    indices, distances = fit_model(df)


# =====================================================================
# HERO
# =====================================================================
st.markdown(
    """
<div class="reco-hero">
    <h1>Recommandations sur-mesure</h1>
    <div class="sub">Choisissez une comédie française — le moteur trouve les 5 films les plus proches.</div>
</div>
<div class="gold-line"></div>
""",
    unsafe_allow_html=True,
)


# =====================================================================
# Sélecteur
# =====================================================================
titres = sorted(df["Titre"].dropna().unique().tolist())

# Préselection : un classique si disponible
default_titles = [
    "Le Fabuleux Destin d'Amélie Poulain",
    "Intouchables",
    "Les Bronzés",
    "OSS 117 : Le Caire, nid d'espions",
]
default_idx = 0
for t in default_titles:
    if t in titres:
        default_idx = titres.index(t)
        break

sel_col1, sel_col2 = st.columns([3, 1])
with sel_col1:
    titre_choisi = st.selectbox(
        "Votre film de référence",
        options=titres,
        index=default_idx,
        help="Tapez le début du titre pour filtrer la liste.",
    )
with sel_col2:
    st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
    n_to_show = st.select_slider(
        "Nombre de recommandations",
        options=[3, 4, 5],
        value=5,
    )


# =====================================================================
# Film sélectionné — carte hero
# =====================================================================
film = df[df["Titre"] == titre_choisi].iloc[0]
genres = [g.strip() for g in str(film.get("Genres", "")).split("|") if g.strip()]
poster = film.get("poster_url") or ""
yt_key_main = best_youtube_key(film)
overview_main = best_overview(film) or "Synopsis non disponible pour le moment."

st.markdown("<div class='selected-card'>", unsafe_allow_html=True)

c_poster, c_info = st.columns([1, 2], gap="large")

with c_poster:
    if isinstance(poster, str) and poster.startswith("http"):
        st.image(poster, use_container_width=True)
    else:
        st.markdown(
            "<div style='aspect-ratio:2/3;background:#111;border-radius:12px;'></div>",
            unsafe_allow_html=True,
        )

with c_info:
    chips_html = "".join(f"<span class='chip'>{g}</span>" for g in genres)
    st.markdown(
        f"""
<div class="selected-title">{film['Titre']}</div>
<div class="selected-meta">
    {int(film['Année'])} · {duration_pretty(film['Durée'])}
    &nbsp;·&nbsp; <span class="note-badge">★ {float(film['Note']):.1f}/10</span>
</div>
<div>{chips_html}</div>
<div class="synopsis">{overview_main}</div>
""",
        unsafe_allow_html=True,
    )

    # Mini-métriques discrètes (intègrent budget/votes en douceur)
    st.markdown(
        f"""
<div class="mini-metrics">
    <div class="metric-tile"><div class="v">{fmt_int(film['Votes'])}</div><div class="l">Votes</div></div>
    <div class="metric-tile"><div class="v">{float(film['Popularité']):.1f}</div><div class="l">Popularité</div></div>
    <div class="metric-tile"><div class="v">{fmt_money(film['Budget'])}</div><div class="l">Budget</div></div>
    <div class="metric-tile"><div class="v">{fmt_money(film['Recette'])}</div><div class="l">Recette</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# Trailer principal embarqué
if yt_key_main:
    with st.expander("Voir la bande-annonce", expanded=False):
        st.video(f"https://www.youtube.com/watch?v={yt_key_main}")


# =====================================================================
# Recommandations
# =====================================================================
st.markdown(
    "<div class='section-title'>Films similaires recommandés</div>",
    unsafe_allow_html=True,
)

recos = reco_film(titre_choisi, df, indices).head(n_to_show)

cols = st.columns(n_to_show, gap="medium")
for rank, (col, (_, r)) in enumerate(zip(cols, recos.iterrows()), start=1):
    with col:
        poster_url = r.get("poster_url") or ""
        if not isinstance(poster_url, str) or not poster_url.startswith("http"):
            poster_url = "https://via.placeholder.com/500x750/111111/F5C518?text=No+poster"

        note = float(r.get("Note") or 0)
        annee = int(r.get("Année") or 0)
        duree = duration_pretty(r.get("Durée"))
        genres_r = " · ".join(
            [g.strip() for g in str(r.get("Genres", "")).split("|") if g.strip()][:2]
        )
        fact_html = fun_fact(r)
        yt_k = best_youtube_key(r)

        if yt_k:
            trailer_html = (
                f"<a class='trailer-btn' href='https://www.youtube.com/watch?v={yt_k}' "
                f"target='_blank' rel='noopener'>Bande-annonce</a>"
            )
        else:
            # Fallback : recherche YouTube
            q = urllib.parse.quote(f"{r['Titre']} bande annonce")
            trailer_html = (
                f"<a class='trailer-btn' href='https://www.youtube.com/results?search_query={q}' "
                f"target='_blank' rel='noopener'>Chercher la bande-annonce</a>"
            )

        card_html = f"""
<div class="reco-card">
    <div class="poster-wrap">
        <img src="{poster_url}" alt="{r['Titre']}" loading="lazy">
        <div class="poster-rank">#{rank}</div>
        <div class="poster-note">★ {note:.1f}</div>
    </div>
    <div class="card-body">
        <div class="card-title">{r['Titre']}</div>
        <div class="card-sub">{annee} · {duree}{(' · ' + genres_r) if genres_r else ''}</div>
        <div class="fun-fact">{fact_html}</div>
        {trailer_html}
    </div>
</div>
"""
        st.markdown(card_html, unsafe_allow_html=True)


# =====================================================================
# Pied de page discret
# =====================================================================
st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.caption(
    f"{len(df):,} films indexés · Modèle NearestNeighbors (cosine) sur Genres TF-IDF + métriques normalisées."
    .replace(",", " ")
)
