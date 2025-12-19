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
        # Créer des onglets pour les différents classements
        tab1, tab2, tab3 = st.tabs(["📊 Classement général", "🏠 Classement domicile", "✈️ Classement extérieur"])
        
        # Fonction pour calculer les statistiques
        def calculate_standings(matches_df, teams_df, match_type='all'):
            team_stats = []
            
            for team_id in teams_df['id'].unique():
                team_name = teams_df[teams_df['id'] == team_id]['name'].iloc[0]
                
                # Initialiser les compteurs
                wins = 0
                draws = 0
                losses = 0
                goals_for = 0
                goals_against = 0
                
                if match_type in ['all', 'home']:
                    # Matchs à domicile
                    home_matches = matches_df[matches_df['home_team_id'] == team_id]
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
                
                if match_type in ['all', 'away']:
                    # Matchs à l'extérieur
                    away_matches = matches_df[matches_df['away_team_id'] == team_id]
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
                
                return standings_df
            else:
                return None
        
        # Onglet 1: Classement général
        with tab1:
            st.markdown("### Classement général")
            standings_df = calculate_standings(matches_df, teams_df, 'all')
            
            if standings_df is not None:
                st.dataframe(
                    standings_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.download_button(
                    label="📥 Télécharger le classement CSV",
                    data=standings_df.to_csv(index=False).encode('utf-8'),
                    file_name='classement_general.csv',
                    mime='text/csv',
                )
            else:
                st.info("Aucun match terminé trouvé.")
        
        # Onglet 2: Classement domicile
        with tab2:
            st.markdown("### Classement domicile")
            home_standings_df = calculate_standings(matches_df, teams_df, 'home')
            
            if home_standings_df is not None:
                st.dataframe(
                    home_standings_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.download_button(
                    label="📥 Télécharger le classement domicile CSV",
                    data=home_standings_df.to_csv(index=False).encode('utf-8'),
                    file_name='classement_domicile.csv',
                    mime='text/csv',
                )
            else:
                st.info("Aucun match à domicile terminé trouvé.")
        
        # Onglet 3: Classement extérieur
        with tab3:
            st.markdown("### Classement extérieur")
            away_standings_df = calculate_standings(matches_df, teams_df, 'away')
            
            if away_standings_df is not None:
                st.dataframe(
                    away_standings_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.download_button(
                    label="📥 Télécharger le classement extérieur CSV",
                    data=away_standings_df.to_csv(index=False).encode('utf-8'),
                    file_name='classement_exterieur.csv',
                    mime='text/csv',
                )
            else:
                st.info("Aucun match à l'extérieur terminé trouvé.")

except Exception as e:
    st.error(f"Erreur lors du chargement des données de classement : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    with st.expander("Détails de l'erreur"):
        st.error(str(e))
