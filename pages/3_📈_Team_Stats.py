"""
Page Statistiques d'équipes - Statistiques détaillées des équipes
"""
import streamlit as st
import pandas as pd
from src.database import get_matches, get_teams, get_player_stats

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
        # Créer des onglets pour différentes statistiques
        tab1, tab2, tab3 = st.tabs(["⚽ Buts marqués", "🥅 Buts encaissés", "🎯 Pourcentage de réussite"])
        
        # Fonction pour calculer les statistiques de buts
        def calculate_goal_stats(matches_df, teams_df):
            goal_stats = []
            
            for team_id in teams_df['id'].unique():
                team_name = teams_df[teams_df['id'] == team_id]['name'].iloc[0]
                
                # Matchs à domicile
                home_matches = matches_df[matches_df['home_team_id'] == team_id]
                # Matchs à l'extérieur
                away_matches = matches_df[matches_df['away_team_id'] == team_id]
                
                # Initialiser les compteurs
                total_goals_for = 0
                total_goals_against = 0
                home_goals_for = 0
                away_goals_for = 0
                home_goals_against = 0
                away_goals_against = 0
                matches_played = 0
                
                # Calculer les buts à domicile
                for _, match in home_matches.iterrows():
                    if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                        home_goals_for += match['final_score_home']
                        home_goals_against += match['final_score_away']
                        total_goals_for += match['final_score_home']
                        total_goals_against += match['final_score_away']
                        matches_played += 1
                
                # Calculer les buts à l'extérieur
                for _, match in away_matches.iterrows():
                    if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                        away_goals_for += match['final_score_away']
                        away_goals_against += match['final_score_home']
                        total_goals_for += match['final_score_away']
                        total_goals_against += match['final_score_home']
                        matches_played += 1
                
                if matches_played > 0:
                    goal_stats.append({
                        'Équipe': team_name,
                        'J': matches_played,
                        'Buts marqués': int(total_goals_for),
                        'Buts encaissés': int(total_goals_against),
                        'Diff': int(total_goals_for - total_goals_against),
                        'Moy marqués': round(total_goals_for / matches_played, 2),
                        'Moy encaissés': round(total_goals_against / matches_played, 2),
                        'Buts dom.': int(home_goals_for),
                        'Buts ext.': int(away_goals_for),
                        'Encaissés dom.': int(home_goals_against),
                        'Encaissés ext.': int(away_goals_against),
                    })
            
            if goal_stats:
                return pd.DataFrame(goal_stats)
            else:
                return None
        
        # Calculer les statistiques
        stats_df = calculate_goal_stats(matches_df, teams_df)
        
        # Onglet 1: Buts marqués
        with tab1:
            st.markdown("### 🏆 Classement des buts marqués")
            
            if stats_df is not None:
                # Trier par buts marqués
                goals_for_df = stats_df[['Équipe', 'J', 'Buts marqués', 'Moy marqués', 'Buts dom.', 'Buts ext.']].copy()
                goals_for_df = goals_for_df.sort_values('Buts marqués', ascending=False).reset_index(drop=True)
                goals_for_df.insert(0, 'Rang', range(1, len(goals_for_df) + 1))
                
                st.dataframe(
                    goals_for_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistiques rapides
                col1, col2, col3 = st.columns(3)
                with col1:
                    best_attack = goals_for_df.iloc[0]
                    st.metric(
                        "Meilleure attaque",
                        best_attack['Équipe'],
                        f"{int(best_attack['Buts marqués'])} buts"
                    )
                with col2:
                    avg_goals = stats_df['Buts marqués'].mean()
                    st.metric(
                        "Moyenne de la ligue",
                        f"{avg_goals:.1f} buts"
                    )
                with col3:
                    total_goals = stats_df['Buts marqués'].sum()
                    st.metric(
                        "Total de buts",
                        f"{int(total_goals)} buts"
                    )
                
                st.download_button(
                    label="📥 Télécharger les statistiques CSV",
                    data=goals_for_df.to_csv(index=False).encode('utf-8'),
                    file_name='stats_buts_marques.csv',
                    mime='text/csv',
                )
            else:
                st.info("Aucun match terminé trouvé.")
        
        # Onglet 2: Buts encaissés
        with tab2:
            st.markdown("### 🛡️ Classement des buts encaissés")
            
            if stats_df is not None:
                # Trier par buts encaissés (ordre croissant = meilleure défense)
                goals_against_df = stats_df[['Équipe', 'J', 'Buts encaissés', 'Moy encaissés', 'Encaissés dom.', 'Encaissés ext.']].copy()
                goals_against_df = goals_against_df.sort_values('Buts encaissés', ascending=True).reset_index(drop=True)
                goals_against_df.insert(0, 'Rang', range(1, len(goals_against_df) + 1))
                
                st.dataframe(
                    goals_against_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistiques rapides
                col1, col2, col3 = st.columns(3)
                with col1:
                    best_defense = goals_against_df.iloc[0]
                    st.metric(
                        "Meilleure défense",
                        best_defense['Équipe'],
                        f"{int(best_defense['Buts encaissés'])} buts encaissés"
                    )
                with col2:
                    avg_goals_against = stats_df['Buts encaissés'].mean()
                    st.metric(
                        "Moyenne de la ligue",
                        f"{avg_goals_against:.1f} buts"
                    )
                with col3:
                    total_goals_against = stats_df['Buts encaissés'].sum()
                    st.metric(
                        "Total de buts encaissés",
                        f"{int(total_goals_against)} buts"
                    )
                
                st.download_button(
                    label="📥 Télécharger les statistiques CSV",
                    data=goals_against_df.to_csv(index=False).encode('utf-8'),
                    file_name='stats_buts_encaisses.csv',
                    mime='text/csv',
                )
            else:
                st.info("Aucun match terminé trouvé.")
        
        # Onglet 3: Pourcentage de réussite
        with tab3:
            st.markdown("### 🎯 Classement du pourcentage de réussite")
            
            if not player_stats_df.empty:
                # Filtrer les joueurs (non officiels)
                players = player_stats_df[player_stats_df['is_official'] == False].copy()
                
                if not players.empty:
                    # Grouper par équipe, match et joueur pour éviter les doublons, puis sommer par équipe
                    # D'abord, grouper par match_id, team_name et player_id pour obtenir les stats uniques
                    unique_stats = players.groupby(['match_id', 'team_name', 'player_id']).agg({
                        'goals': 'max',  # Utiliser max au cas où il y aurait des doublons
                        'shots': 'max'
                    }).reset_index()
                    
                    # Ensuite, grouper par équipe et sommer tous les matchs
                    shooting_stats = unique_stats.groupby('team_name').agg({
                        'goals': 'sum',
                        'shots': 'sum'
                    }).reset_index()
                    
                    # Filtrer les équipes avec au moins 1 tir
                    shooting_stats = shooting_stats[shooting_stats['shots'] > 0].copy()
                    
                    # Calculer le pourcentage de réussite
                    shooting_stats['% Réussite'] = (
                        (shooting_stats['goals'] / shooting_stats['shots'] * 100)
                        .round(2)
                    )
                    
                    # Renommer les colonnes
                    shooting_stats = shooting_stats.rename(columns={
                        'team_name': 'Équipe',
                        'goals': 'Buts',
                        'shots': 'Tirs'
                    })
                    
                    # Trier par pourcentage de réussite
                    shooting_stats = shooting_stats.sort_values('% Réussite', ascending=False).reset_index(drop=True)
                    shooting_stats.insert(0, 'Rang', range(1, len(shooting_stats) + 1))
                    
                    # Réorganiser les colonnes pour mettre % Réussite après Équipe
                    shooting_stats = shooting_stats[['Rang', 'Équipe', '% Réussite', 'Buts', 'Tirs']]
                    
                    st.dataframe(
                        shooting_stats,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Statistiques rapides
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        best_shooting = shooting_stats.iloc[0]
                        st.metric(
                            "Meilleur % de réussite",
                            best_shooting['Équipe'],
                            f"{best_shooting['% Réussite']:.2f}%"
                        )
                    with col2:
                        avg_shooting = shooting_stats['% Réussite'].mean()
                        st.metric(
                            "Moyenne de la ligue",
                            f"{avg_shooting:.2f}%"
                        )
                    with col3:
                        total_shots = shooting_stats['Tirs'].sum()
                        st.metric(
                            "Total de tirs",
                            f"{int(total_shots)}"
                        )
                    
                    st.download_button(
                        label="📥 Télécharger les statistiques CSV",
                        data=shooting_stats.to_csv(index=False).encode('utf-8'),
                        file_name='stats_pourcentage_reussite.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("Aucune statistique de joueur disponible.")
            else:
                st.info("Aucune statistique de joueur disponible.")

except Exception as e:
    st.error(f"Erreur lors du chargement des statistiques : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    with st.expander("Détails de l'erreur"):
        st.error(str(e))
