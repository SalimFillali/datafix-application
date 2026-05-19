"""Page A propos - DATAFIX."""
from pathlib import Path
import streamlit as st
from utils.theme import inject_global_css, hero_header

st.set_page_config(page_title="DATAFIX – À propos", layout="wide")
inject_global_css()

ASSETS = Path(__file__).resolve().parent.parent / "assets"
LOGO = ASSETS / "logo.png"

with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)
    st.caption("L'équipe et la méthodologie")

hero_header(
    title="À <span class='accent-text'>propos</span>",
    subtitle="L'équipe DATAFIX et sa méthode.",
)

st.markdown(
    """<div class="datafix-tagline">
        <strong>DATAFIX</strong> est un projet pédagogique mené dans le cadre
        de la formation Data Analyst. L'objectif : livrer un outil opérationnel
        à un futur cinéma indépendant en Creuse, avec un positionnement éditorial
        affirmé. Notre choix : la <strong>comédie française post-1980</strong>,
        sélectionnée sur la qualité (note TMDB ≥ 6.5/10).
    </div>""",
    unsafe_allow_html=True,
)

st.write("")
st.write("")

# --- L'équipe : 5 personnes, traitées équitablement ----------------- #
st.subheader("L'équipe")
st.write("")

team = [
    ("Romain",   "Scrum Master",   "Coordination des sprints et animation des cérémonies agiles."),
    ("Salim",    "Product Owner",  "Vision produit, priorisation du backlog et lien avec le client."),
    ("Gatien",   "Code Reviewer",  "Revue de code, qualité, bonnes pratiques et intégration."),
    ("Jade",     "Team Member",    "Mots-clés, NLP et enrichissement du dataset."),
    ("Liliana",  "Team Member",    "Distribution, visualisations et analyses."),
]

cols = st.columns(5, gap="medium")
for col, (name, role, mission) in zip(cols, team):
    photo_path = ASSETS / f"photo_{name.lower()}.png"
    with col:
        if photo_path.exists():
            sub = st.columns([1, 3, 1])
            with sub[1]:
                st.image(str(photo_path), use_container_width=True)
        st.markdown(
            f"""<div class="datafix-card-clean" style="text-align:center; margin-top:0.5rem;">
              <div class="num">{role.upper()}</div>
              <div class="title">{name}</div>
              <div class="text">{mission}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.write("")
st.divider()

# --- Notre méthode -------------------------------------------------- #
st.subheader("Notre méthode")
st.markdown(
    """
1. **Comprendre le besoin :** échanges avec le client et étude de marché du cinéma rural en Creuse.
2. **Définir la ligne éditoriale :** comédie française sortie après 1980, notée 6.5/10 ou plus.
3. **Collecter les données :** titres et notes depuis IMDb, affiches et synopsis depuis TMDB.
4. **Nettoyer et filtrer :** fusion des deux sources via les identifiants `tconst` et `tmdb_id`, puis application des critères métier.
5. **Modéliser :** vectorisation TF-IDF en français des genres et synopsis, puis calcul de similarité cosinus.
6. **Prototyper :** maquette sur Figma, puis développement de l'application Streamlit.
7. **Livrer :** démonstration au client et documentation pour permettre la reprise du projet.
    """
)

st.subheader("Critères de sélection du catalogue")
st.markdown(
    """
- **Production française :** pour ancrer le cinéma dans son territoire et soutenir la création nationale.
- **Sortie après 1980 :** un cinéma vivant, qui parle directement aux générations d'aujourd'hui.
- **Genre comédie :** un registre fédérateur, capable de rassembler toutes les générations en zone rurale.
- **Note minimale de 6.5/10 sur TMDB :** un gage de qualité, validé par des dizaines de milliers de spectateurs.
    """
)

st.divider()
st.subheader("Stack technique")
s1, s2, s3 = st.columns(3, gap="large")
with s1:
    st.markdown(
        """<div class="datafix-card-clean">
          <div class="num">01 / Données</div>
          <div class="title">Python · Pandas</div>
          <div class="text">Manipulation des données, fusion des sources IMDb et TMDB.</div>
        </div>""",
        unsafe_allow_html=True,
    )
with s2:
    st.markdown(
        """<div class="datafix-card-clean">
          <div class="num">02 / Modèle</div>
          <div class="title">scikit-learn</div>
          <div class="text">TF-IDF et similarité cosinus pour le moteur de recommandation.</div>
        </div>""",
        unsafe_allow_html=True,
    )
with s3:
    st.markdown(
        """<div class="datafix-card-clean">
          <div class="num">03 / Interface</div>
          <div class="title">Streamlit · TMDB API</div>
          <div class="text">Interface multipage et affiches officielles en temps réel.</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.write("")
st.caption("© 2026 DATAFIX · Sprint 4 · Wild Code School")
