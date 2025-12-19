"""
Tableau de Bord Handball - Application Principale
"""
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Handball",
    page_icon="🤾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar menu
with st.sidebar:
    st.markdown("## 🤾 Navigation")
    st.markdown("---")
    
    st.markdown("### 📊 Pages disponibles")
    st.page_link("app.py", label="Accueil", icon="🏠")
    st.page_link("pages/2_🏆_Rankings.py", label="Classements", icon="🏆")
    
    st.markdown("---")
    st.markdown("### 📈 À venir")
    st.markdown("""
    - Ligues
    - Équipes
    - Joueurs
    - Matchs
    - Statistiques avancées
    """)

# CSS personnalisé
st.markdown("""
    <style>
    /* Cacher la navigation par défaut de Streamlit */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 3rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .feature-box {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Contenu principal
st.markdown('<div class="main-header">🤾 Dashboard Handball</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analyse et visualisation complète des données de matchs de handball</div>', unsafe_allow_html=True)

# Section statistiques rapides
st.write("---")
st.markdown("### 📊 Overview")

try:
    from src.database import get_leagues, get_teams, get_players, get_matches
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        leagues_df = get_leagues()
        st.metric("Championnats", len(leagues_df))
    
    with col2:
        teams_df = get_teams()
        st.metric("Équipes", len(teams_df))
    
    with col3:
        players_df = get_players()
        st.metric("Joueurs", len(players_df))
    
    with col4:
        matches_df = get_matches()
        st.metric("Matchs", len(matches_df))

except Exception as e:
    st.warning("⚠️ Impossible de charger les statistiques de la base de données. Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    st.info("💡 Créez un fichier `.env` dans le répertoire racine avec vos identifiants Supabase. Voir `.env.example` pour le format requis.")
    with st.expander("Détails de l'erreur"):
        st.error(str(e))

# Section fonctionnalités
st.write("---")
st.markdown("### 🎯 Fonctionnalités du tableau de bord")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h4>📈 Exploration des données</h4>
        <ul>
            <li>Parcourir les ligues, équipes et joueurs</li>
            <li>Voir les résultats et statistiques des matchs</li>
            <li>Analyser les performances des joueurs</li>
            <li>Suivre les actions et événements de matchs</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h4>🔍 Analyses avancées</h4>
        <ul>
            <li>Outils de comparaison des joueurs</li>
            <li>Tendances de performance des équipes</li>
            <li>Insights statistiques</li>
            <li>Filtrage personnalisé des données</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h4>📊 Visualisations</h4>
        <ul>
            <li>Graphiques et diagrammes interactifs</li>
            <li>Analyse chronologique des matchs</li>
            <li>Cartes de chaleur de performance</li>
            <li>Distributions statistiques</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h4>⚙️ Structure de la base de données</h4>
        <ul>
            <li>Ligues : Informations sur les compétitions</li>
            <li>Équipes : Profils des équipes</li>
            <li>Joueurs : Profils des joueurs et associations aux équipes</li>
            <li>Matchs : Résultats et scores des parties</li>
            <li>Stats Joueurs : Métriques de performance détaillées</li>
            <li>Actions : Événements chronologiques des matchs</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Pied de page
st.write("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>Créé avec Streamlit 🎈 | Données par Supabase 🚀</p>
</div>
""", unsafe_allow_html=True)
