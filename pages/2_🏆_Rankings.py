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
    st.page_link("pages/3_📈_Team_Stats.py", label="Statistiques d'équipes", icon="📈")
    st.page_link("pages/4_👤_Player_Stats.py", label="Statistiques de joueurs", icon="👤")
    
    st.markdown("---")
    st.info("**Page actuelle:** Classements")

st.title("🏆 Classements")

try:
    # Charger les données
    matches_df = get_matches()
    teams_df = get_teams()
    
    if matches_df.empty:
        st.info("Aucune donnée de match disponible. Importez des matchs pour voir les classements !")
    else:
        # Créer des onglets pour les différents classements
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Classement général", "🏠 Classement domicile", "✈️ Classement extérieur", "⏱️ Classement mi-temps"])
        
        # Fonction pour calculer les statistiques
        def calculate_standings(matches_df, teams_df, match_type='all', score_type='final'):
            team_stats = []
            
            for team_id in teams_df['id'].unique():
                team_name = teams_df[teams_df['id'] == team_id]['name'].iloc[0]
                
                # Initialiser les compteurs
                wins = 0
                draws = 0
                losses = 0
                goals_for = 0
                goals_against = 0
                
                # Sélectionner les colonnes de score appropriées
                if score_type == 'halftime':
                    home_score_col = 'ht_score_home'
                    away_score_col = 'ht_score_away'
                else:
                    home_score_col = 'final_score_home'
                    away_score_col = 'final_score_away'
                
                if match_type in ['all', 'home']:
                    # Matchs à domicile
                    home_matches = matches_df[matches_df['home_team_id'] == team_id]
                    for _, match in home_matches.iterrows():
                        if pd.notna(match[home_score_col]) and pd.notna(match[away_score_col]):
                            goals_for += match[home_score_col]
                            goals_against += match[away_score_col]
                            
                            if match[home_score_col] > match[away_score_col]:
                                wins += 1
                            elif match[home_score_col] == match[away_score_col]:
                                draws += 1
                            else:
                                losses += 1
                
                if match_type in ['all', 'away']:
                    # Matchs à l'extérieur
                    away_matches = matches_df[matches_df['away_team_id'] == team_id]
                    for _, match in away_matches.iterrows():
                        if pd.notna(match[home_score_col]) and pd.notna(match[away_score_col]):
                            goals_for += match[away_score_col]
                            goals_against += match[home_score_col]
                            
                            if match[away_score_col] > match[home_score_col]:
                                wins += 1
                            elif match[away_score_col] == match[home_score_col]:
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
        
        # Onglet 4: Classement mi-temps
        with tab4:
            st.markdown("### Classement mi-temps")
            st.info("Classement basé sur les scores à la mi-temps")
            halftime_standings_df = calculate_standings(matches_df, teams_df, 'all', 'halftime')
            
            if halftime_standings_df is not None:
                st.dataframe(
                    halftime_standings_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.download_button(
                    label="📥 Télécharger le classement mi-temps CSV",
                    data=halftime_standings_df.to_csv(index=False).encode('utf-8'),
                    file_name='classement_mi_temps.csv',
                    mime='text/csv',
                )
            else:
                st.info("Aucun match avec score mi-temps disponible.")

except Exception as e:
    st.error(f"Erreur lors du chargement des données de classement : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    with st.expander("Détails de l'erreur"):
        st.error(str(e))
