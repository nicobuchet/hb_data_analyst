"""
Page Statistiques d'équipes - Statistiques détaillées des équipes
"""
import streamlit as st
import pandas as pd
from src.database import get_matches, get_teams, get_player_stats
from src.pages.team_stats import (
    tab_goals_scored,
    tab_goals_conceded,
    tab_shooting_percentage,
    tab_saves,
    tab_7m_goals,
    tab_sanctions
)
from src.pages.team_stats.utils import calculate_goal_stats

st.set_page_config(page_title="Statistiques d'équipes", page_icon="📈", layout="wide")

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
    st.info("**Page actuelle:** Statistiques d'équipes")

st.title("📈 Statistiques d'équipes")
st.write("Consultez les statistiques détaillées des équipes.")

try:
    # Charger les données
    matches_df = get_matches()
    teams_df = get_teams()
    player_stats_df = get_player_stats()
    
    if matches_df.empty:
        st.info("Aucune donnée de match disponible. Importez des matchs pour voir les statistiques !")
    else:
        # Calculer les statistiques de buts pour les onglets qui en ont besoin
        stats_df = calculate_goal_stats(matches_df, teams_df)
        
        # Créer des onglets pour différentes statistiques
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "⚽ Buts marqués", 
            "🥅 Buts encaissés", 
            "🎯 Pourcentage de réussite", 
            "🧤 Arrêts", 
            "🎯 Buts 7m", 
            "⚠️ Sanctions"
        ])
        
        with tab1:
            tab_goals_scored.render(matches_df, teams_df, player_stats_df, stats_df)
        
        with tab2:
            tab_goals_conceded.render(matches_df, teams_df, player_stats_df, stats_df)
        
        with tab3:
            tab_shooting_percentage.render(matches_df, teams_df, player_stats_df, stats_df)
        
        with tab4:
            tab_saves.render(matches_df, teams_df, player_stats_df, stats_df)
        
        with tab5:
            tab_7m_goals.render(matches_df, teams_df, player_stats_df, stats_df)
        
        with tab6:
            tab_sanctions.render(matches_df, teams_df, player_stats_df, stats_df)

except Exception as e:
    st.error(f"Erreur lors du chargement des statistiques : {e}")
    import traceback
    st.error(traceback.format_exc())
