"""
Page Classements - Voir les classements des équipes et joueurs
"""
import streamlit as st
import pandas as pd
from src.database import get_matches, get_player_stats, get_teams

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
st.write("Consultez les classements des équipes et les statistiques des joueurs.")

try:
    # Créer des onglets pour différents types de classements
    tab1, tab2, tab3 = st.tabs(["🏅 Classement des équipes", "⚽ Meilleurs buteurs", "🥅 Meilleurs gardiens"])
    
    # Charger les données
    matches_df = get_matches()
    player_stats_df = get_player_stats()
    teams_df = get_teams()
    
    if matches_df.empty:
        st.info("Aucune donnée de match disponible. Importez des matchs pour voir les classements !")
    else:
        # Onglet 1: Classement des équipes
        with tab1:
            st.markdown("### Classement des équipes")
            
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
                points = (wins * 2) + draws  # Système de notation standard : 2 pour victoire, 1 pour nul
                
                if games_played > 0:
                    team_stats.append({
                        'Équipe': team_name,
                        'J': games_played,
                        'V': wins,
                        'N': draws,
                        'D': losses,
                        'BP': int(goals_for),
                        'BC': int(goals_against),
                        'Diff': int(goals_for - goals_against),
                        'Pts': points
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
        
        # Onglet 2: Meilleurs buteurs
        with tab2:
            st.markdown("### Meilleurs buteurs")
            
            if not player_stats_df.empty:
                # Filtrer les officiels et calculer les buts totaux
                players = player_stats_df[player_stats_df['is_official'] == False].copy()
                
                if not players.empty:
                    # Grouper par joueur et sommer les buts
                    scorer_stats = players.groupby(['player_name', 'team_name']).agg({
                        'goals': 'sum',
                        'shots': 'sum',
                        'goals_7m': 'sum'
                    }).reset_index()
                    
                    # Calculer le pourcentage de réussite
                    scorer_stats['% Réussite'] = (
                        (scorer_stats['goals'] / scorer_stats['shots'] * 100)
                        .fillna(0)
                        .round(1)
                    )
                    
                    # Filtrer les joueurs avec au moins 1 but
                    scorer_stats = scorer_stats[scorer_stats['goals'] > 0]
                    
                    # Trier par buts
                    scorer_stats = scorer_stats.sort_values('goals', ascending=False).reset_index(drop=True)
                    
                    # Ajouter le rang
                    scorer_stats.insert(0, 'Rang', range(1, len(scorer_stats) + 1))
                    
                    # Renommer les colonnes
                    scorer_stats = scorer_stats.rename(columns={
                        'player_name': 'Joueur',
                        'team_name': 'Équipe',
                        'goals': 'Buts',
                        'shots': 'Tirs',
                        'goals_7m': 'Buts 7m'
                    })
                    
                    # Afficher le top 20
                    st.dataframe(
                        scorer_stats.head(20),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Option de téléchargement
                    st.download_button(
                        label="📥 Télécharger les meilleurs buteurs CSV",
                        data=scorer_stats.to_csv(index=False).encode('utf-8'),
                        file_name='meilleurs_buteurs.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("Aucune statistique de joueur disponible.")
            else:
                st.info("Aucune statistique de joueur disponible.")
        
        # Onglet 3: Meilleurs gardiens
        with tab3:
            st.markdown("### Meilleurs gardiens")
            
            if not player_stats_df.empty:
                # Filtrer les gardiens (joueurs avec arrêts > 0)
                goalkeepers = player_stats_df[
                    (player_stats_df['is_official'] == False) & 
                    (player_stats_df['saves'] > 0)
                ].copy()
                
                if not goalkeepers.empty:
                    # Grouper par joueur et sommer les stats
                    gk_stats = goalkeepers.groupby(['player_name', 'team_name']).agg({
                        'saves': 'sum'
                    }).reset_index()
                    
                    # Trier par arrêts
                    gk_stats = gk_stats.sort_values('saves', ascending=False).reset_index(drop=True)
                    
                    # Ajouter le rang
                    gk_stats.insert(0, 'Rang', range(1, len(gk_stats) + 1))
                    
                    # Renommer les colonnes
                    gk_stats = gk_stats.rename(columns={
                        'player_name': 'Joueur',
                        'team_name': 'Équipe',
                        'saves': 'Arrêts'
                    })
                    
                    # Afficher le top 20
                    st.dataframe(
                        gk_stats.head(20),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Option de téléchargement
                    st.download_button(
                        label="📥 Télécharger les meilleurs gardiens CSV",
                        data=gk_stats.to_csv(index=False).encode('utf-8'),
                        file_name='meilleurs_gardiens.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("Aucune statistique de gardien disponible.")
            else:
                st.info("Aucune statistique de gardien disponible.")

except Exception as e:
    st.error(f"Erreur lors du chargement des données de classement : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    with st.expander("Détails de l'erreur"):
        st.error(str(e))

try:
    # Create tabs for different ranking types
    tab1, tab2, tab3 = st.tabs(["🏅 Team Standings", "⚽ Top Scorers", "🥅 Top Goalkeepers"])
    
    # Load data
    matches_df = get_matches()
    player_stats_df = get_player_stats()
    teams_df = get_teams()
    
    if matches_df.empty:
        st.info("No match data available yet. Upload some matches to see rankings!")
    else:
        # Tab 1: Team Standings
        with tab1:
            st.markdown("### Team Standings")
            
            # Calculate team statistics
            team_stats = []
            
            for team_id in teams_df['id'].unique():
                team_name = teams_df[teams_df['id'] == team_id]['name'].iloc[0]
                
                # Home matches
                home_matches = matches_df[matches_df['home_team_id'] == team_id]
                # Away matches
                away_matches = matches_df[matches_df['away_team_id'] == team_id]
                
                # Initialize counters
                wins = 0
                draws = 0
                losses = 0
                goals_for = 0
                goals_against = 0
                
                # Calculate home results
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
                
                # Calculate away results
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
                points = (wins * 2) + draws  # Standard handball scoring: 2 for win, 1 for draw
                
                if games_played > 0:
                    team_stats.append({
                        'Team': team_name,
                        'Played': games_played,
                        'Won': wins,
                        'Drawn': draws,
                        'Lost': losses,
                        'Goals For': int(goals_for),
                        'Goals Against': int(goals_against),
                        'Goal Diff': int(goals_for - goals_against),
                        'Points': points
                    })
            
            if team_stats:
                standings_df = pd.DataFrame(team_stats)
                # Sort by points, then goal difference, then goals for
                standings_df = standings_df.sort_values(
                    by=['Points', 'Goal Diff', 'Goals For'], 
                    ascending=[False, False, False]
                ).reset_index(drop=True)
                
                # Add rank column
                standings_df.insert(0, 'Rank', range(1, len(standings_df) + 1))
                
                # Display with styling
                st.dataframe(
                    standings_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download option
                st.download_button(
                    label="📥 Download Standings CSV",
                    data=standings_df.to_csv(index=False).encode('utf-8'),
                    file_name='team_standings.csv',
                    mime='text/csv',
                )
            else:
                st.info("No completed matches found.")
        
        # Tab 2: Top Scorers
        with tab2:
            st.markdown("### Top Scorers")
            
            if not player_stats_df.empty:
                # Filter out officials and calculate total goals
                players = player_stats_df[player_stats_df['is_official'] == False].copy()
                
                if not players.empty:
                    # Group by player and sum goals
                    scorer_stats = players.groupby(['player_name', 'team_name']).agg({
                        'goals': 'sum',
                        'shots': 'sum',
                        'goals_7m': 'sum'
                    }).reset_index()
                    
                    # Calculate shooting percentage
                    scorer_stats['Shot %'] = (
                        (scorer_stats['goals'] / scorer_stats['shots'] * 100)
                        .fillna(0)
                        .round(1)
                    )
                    
                    # Filter players with at least 1 goal
                    scorer_stats = scorer_stats[scorer_stats['goals'] > 0]
                    
                    # Sort by goals
                    scorer_stats = scorer_stats.sort_values('goals', ascending=False).reset_index(drop=True)
                    
                    # Add rank
                    scorer_stats.insert(0, 'Rank', range(1, len(scorer_stats) + 1))
                    
                    # Rename columns
                    scorer_stats = scorer_stats.rename(columns={
                        'player_name': 'Player',
                        'team_name': 'Team',
                        'goals': 'Goals',
                        'shots': 'Shots',
                        'goals_7m': '7m Goals'
                    })
                    
                    # Display top 20
                    st.dataframe(
                        scorer_stats.head(20),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Download option
                    st.download_button(
                        label="📥 Download Top Scorers CSV",
                        data=scorer_stats.to_csv(index=False).encode('utf-8'),
                        file_name='top_scorers.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("No player statistics available.")
            else:
                st.info("No player statistics available.")
        
        # Tab 3: Top Goalkeepers
        with tab3:
            st.markdown("### Top Goalkeepers")
            
            if not player_stats_df.empty:
                # Filter goalkeepers (players with saves > 0)
                goalkeepers = player_stats_df[
                    (player_stats_df['is_official'] == False) & 
                    (player_stats_df['saves'] > 0)
                ].copy()
                
                if not goalkeepers.empty:
                    # Group by player and sum stats
                    gk_stats = goalkeepers.groupby(['player_name', 'team_name']).agg({
                        'saves': 'sum'
                    }).reset_index()
                    
                    # Sort by saves
                    gk_stats = gk_stats.sort_values('saves', ascending=False).reset_index(drop=True)
                    
                    # Add rank
                    gk_stats.insert(0, 'Rank', range(1, len(gk_stats) + 1))
                    
                    # Rename columns
                    gk_stats = gk_stats.rename(columns={
                        'player_name': 'Player',
                        'team_name': 'Team',
                        'saves': 'Saves'
                    })
                    
                    # Display top 20
                    st.dataframe(
                        gk_stats.head(20),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Download option
                    st.download_button(
                        label="📥 Download Top Goalkeepers CSV",
                        data=gk_stats.to_csv(index=False).encode('utf-8'),
                        file_name='top_goalkeepers.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("No goalkeeper statistics available.")
            else:
                st.info("No goalkeeper statistics available.")

except Exception as e:
    st.error(f"Error loading rankings data: {str(e)}")
    st.info("Please ensure your Supabase connection is properly configured.")
    with st.expander("Error details"):
        st.error(str(e))
