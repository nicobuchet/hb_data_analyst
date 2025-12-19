"""
Page Statistiques d'équipes - Statistiques détaillées des équipes
"""
import streamlit as st
import pandas as pd
from src.database import get_matches, get_teams

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
    
    if matches_df.empty:
        st.info("Aucune donnée de match disponible. Importez des matchs pour voir les statistiques !")
    else:
        # Créer des onglets pour différentes statistiques
        tab1, tab2 = st.tabs(["⚽ Buts marqués", "🥅 Buts encaissés"])
        
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

except Exception as e:
    st.error(f"Erreur lors du chargement des statistiques : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    with st.expander("Détails de l'erreur"):
        st.error(str(e))
