"""
Page Classements - Voir les classements des équipes et joueurs
"""
import streamlit as st
import pandas as pd
from src.database import get_matches, get_teams

st.set_page_config(page_title="Classements", page_icon="🏆", layout="wide")

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
    
    st.markdown("---")
    st.info("**Page actuelle:** Classements")

st.title("🏆 Classements")
st.write("Consultez le classement de la ligue.")

try:
    # Charger les données
    matches_df = get_matches()
    teams_df = get_teams()
    
    if matches_df.empty:
        st.info("Aucune donnée de match disponible. Importez des matchs pour voir les classements !")
    else:
        st.markdown("### Classement de la ligue")
        
        # Calculer les statistiques des équipes
        team_stats = []
        
        for team_id in teams_df['id'].unique():
            team_name = teams_df[teams_df['id'] == team_id]['name'].iloc[0]
            
            # Matchs à domicile
            home_matches = matches_df[matches_df['home_team_id'] == team_id]
            # Matchs à l'extérieur
            away_matches = matches_df[matches_df['away_team_id'] == team_id]
            
            # Initialiser les compteurs
            wins = 0
            draws = 0
            losses = 0
            goals_for = 0
            goals_against = 0
            
            # Calculer les résultats à domicile
            for _, match in home_matches.iterrows():
                if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                    goals_for += match['final_score_home']
                    goals_against += match['final_score_away']
                    
                    if match['final_score_home'] > match['final_score_away']:
                        wins += 1
                    elif match['final_score_home'] == match['final_score_away']:
                        draws += 1
                    else:
                        losses += 1
            
            # Calculer les résultats à l'extérieur
            for _, match in away_matches.iterrows():
                if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                    goals_for += match['final_score_away']
                    goals_against += match['final_score_home']
                    
                    if match['final_score_away'] > match['final_score_home']:
                        wins += 1
                    elif match['final_score_away'] == match['final_score_home']:
                        draws += 1
                    else:
                        losses += 1
            
            games_played = wins + draws + losses
            points = (wins * 3) + (draws * 2) + (losses * 1)  # Victoire = 3pts, Nul = 2pts, Défaite = 1pt
            
            if games_played > 0:
                team_stats.append({
                    'Équipe': team_name,
                    'Pts': points,
                    'J': games_played,
                    'V': wins,
                    'N': draws,
                    'D': losses,
                    'BP': int(goals_for),
                    'BC': int(goals_against),
                    'Diff': int(goals_for - goals_against),
                })
        
        if team_stats:
            standings_df = pd.DataFrame(team_stats)
            # Trier par points, puis différence de buts, puis buts pour
            standings_df = standings_df.sort_values(
                by=['Pts', 'Diff', 'BP'], 
                ascending=[False, False, False]
            ).reset_index(drop=True)
            
            # Ajouter la colonne rang
            standings_df.insert(0, 'Rang', range(1, len(standings_df) + 1))
            
            # Afficher avec style
            st.dataframe(
                standings_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Option de téléchargement
            st.download_button(
                label="📥 Télécharger le classement CSV",
                data=standings_df.to_csv(index=False).encode('utf-8'),
                file_name='classement_equipes.csv',
                mime='text/csv',
            )
        else:
            st.info("Aucun match terminé trouvé.")

except Exception as e:
    st.error(f"Erreur lors du chargement des données de classement : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    with st.expander("Détails de l'erreur"):
        st.error(str(e))
