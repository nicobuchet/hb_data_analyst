"""
Page Statistiques de joueurs - Statistiques individuelles des joueurs
"""
import streamlit as st
from src.database import get_player_stats, get_matches, get_teams
from src.pages.player_stats import (
    tab_goal_scorers,
    tab_goalkeepers,
    tab_7m_ranking,
    tab_best_performances,
    tab_best_7m_performances,
    tab_best_goalkeeper_performances
)

st.set_page_config(page_title="Statistiques de joueurs", page_icon="👤", layout="wide")

# Cacher la navigation par défaut de Streamlit
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🤾 Navigation")
    st.markdown("---")
    
    st.page_link("app.py", label="Accueil", icon="🏠")
    st.page_link("pages/2_🏆_Rankings.py", label="Classements", icon="🏆")
    st.page_link("pages/3_📈_Team_Stats.py", label="Statistiques d'équipes", icon="📈")
    st.page_link("pages/4_👤_Player_Stats.py", label="Statistiques de joueurs", icon="👤")
    
    st.markdown("---")
    st.info("**Page actuelle:** Statistiques de joueurs")

st.title("👤 Statistiques de joueurs")
st.write("Consultez les statistiques individuelles des joueurs.")

try:
    # Charger les données
    player_stats_df = get_player_stats()
    matches_df = get_matches()
    teams_df = get_teams()
    
    if player_stats_df.empty:
        st.info("Aucune donnée de joueur disponible. Importez des matchs pour voir les statistiques !")
    else:
        # Créer des onglets pour différentes statistiques
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "⚽ Classement des buteurs", 
            "🧤 Classement des gardiens", 
            "🎯 Classement des 7m",
            "🌟 Meilleures performances",
            "🎯 Meilleures perf. 7m",
            "🧤 Meilleures perf. gardiens"
        ])
        
        # Onglet 1: Classement des buteurs
        with tab1:
            tab_goal_scorers.render(player_stats_df, matches_df, teams_df)
        
        # Onglet 2: Classement des gardiens
        with tab2:
            tab_goalkeepers.render(player_stats_df, matches_df, teams_df)
        
        # Onglet 3: Classement des 7m
        with tab3:
            tab_7m_ranking.render(player_stats_df, matches_df, teams_df)
        
        # Onglet 4: Meilleures performances
        with tab4:
            tab_best_performances.render(player_stats_df, matches_df, teams_df)
        
        # Onglet 5: Meilleures performances 7m
        with tab5:
            tab_best_7m_performances.render(player_stats_df, matches_df, teams_df)
        
        # Onglet 6: Meilleures performances gardiens
        with tab6:
            tab_best_goalkeeper_performances.render(player_stats_df, matches_df, teams_df)

except Exception as e:
    st.error(f"Erreur lors du chargement des statistiques : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    with st.expander("Détails de l'erreur"):
        st.error(str(e))
