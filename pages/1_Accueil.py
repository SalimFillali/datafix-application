"""Page Accueil - DATAFIX."""

import streamlit as st

st.set_page_config(page_title="DATAFIX – Accueil", layout="wide")

st.markdown(
    """
    <style>
    .datafix-title {
        text-align: center;
        font-size: 4rem;
        font-weight: 800;
        margin-top: 2rem;
    }

    .datafix-subtitle {
        text-align: center;
        color: #9A9AA0;
        font-size: 1.2rem;
        margin-top: -0.5rem;
    }

    .gold-line {
        width: 84px;
        height: 4px;
        background: #F5C518;
        border-radius: 4px;
        margin: 1rem auto 2rem auto;
    }

    .datafix-tagline {
        text-align: center;
        font-size: 1.25rem;
        line-height: 1.8;
        max-width: 950px;
        margin: auto;
        padding: 1.5rem;
        border-radius: 18px;
        background: rgba(245, 197, 24, 0.08);
    }

    .datafix-card-clean {
        padding: 1.5rem;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.10);
        min-height: 230px;
    }

    .num {
        color: #F5C518;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }

    .title {
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 0.8rem;
    }

    .text {
        color: #B8B8B8;
        font-size: 1rem;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.caption("v0.2 · Sprint 4 · 2026")

st.markdown("<div class='datafix-title'>DATAFIX</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="datafix-subtitle">
        La comédie française, sublimée par la data.
    </div>
    <div class="gold-line"></div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="datafix-tagline">
        DATAFIX accompagne le futur cinéma de la <strong>Creuse</strong> avec
        un moteur de recommandation dédié aux meilleures
        <strong>comédies françaises</strong>. Découvrez des films cultes et
        trouvez facilement votre prochaine séance idéale.
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.write("")

st.subheader("Que pouvez-vous faire ici ?")

st.write("")

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown(
        """
        <div class="datafix-card-clean">
          <div class="num">01 / Recommandation</div>
          <div class="title">Recommander une comédie</div>
          <div class="text">
            Choisissez Intouchables, Amélie Poulain, Astérix… vous obtenez
            instantanément des comédies françaises proches.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="datafix-card-clean">
          <div class="num">02 / Catalogue</div>
          <div class="title">Explorer le catalogue FR</div>
          <div class="text">
            Explorez les comédies françaises sélectionnées, leurs notes,
            leurs années et leurs informations principales.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div class="datafix-card-clean">
          <div class="num">03 / Équipe</div>
          <div class="title">À propos</div>
          <div class="text">
            Découvrez l'équipe DATAFIX, la méthodologie et la stack technique
            utilisée pour construire l'application.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")
st.write("")

if st.button("Démarrer une recommandation", use_container_width=True, type="primary"):
    st.success("La page recommandation arrive bientôt ")