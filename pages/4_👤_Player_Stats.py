"""
Page Statistiques de joueurs - Statistiques individuelles des joueurs
"""
import streamlit as st
import pandas as pd
from src.database import get_player_stats, get_matches

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
    
    if player_stats_df.empty:
        st.info("Aucune donnée de joueur disponible. Importez des matchs pour voir les statistiques !")
    else:
        # Créer des onglets pour différentes statistiques
        tab1, tab2 = st.tabs(["⚽ Classement des buteurs", "🧤 Classement des gardiens"])
        
        # Onglet 1: Classement des buteurs
        with tab1:
            st.markdown("### ⚽ Classement général des buteurs")
            
            # Filtrer les joueurs (non officiels)
            players = player_stats_df[player_stats_df['is_official'] == False].copy()
            
            if not players.empty:
                # D'abord, calculer le nombre de matchs joués par joueur en comptant tous les matchs
                # où ils ont une entrée dans player_stats (peu importe les stats)
                matches_per_player = players.groupby(['player_name', 'team_name']).agg({
                    'match_id': 'nunique'
                }).reset_index()
                matches_per_player = matches_per_player.rename(columns={'match_id': 'matches_played'})
                
                # Grouper par joueur et équipe, sommer les statistiques
                player_goals_stats = players.groupby(['player_name', 'team_name']).agg({
                    'goals': 'sum',
                    'shots': 'sum',
                    'goals_7m': 'sum'
                }).reset_index()
                
                # Fusionner avec le nombre de matchs
                player_goals_stats = player_goals_stats.merge(
                    matches_per_player,
                    on=['player_name', 'team_name'],
                    how='left'
                )
                
                # Filtrer les joueurs avec au moins 1 but
                player_goals_stats = player_goals_stats[player_goals_stats['goals'] > 0].copy()
                
                # Calculer le pourcentage de réussite
                player_goals_stats['% Réussite'] = player_goals_stats.apply(
                    lambda row: round(row['goals'] / row['shots'] * 100, 2) if row['shots'] > 0 else 0,
                    axis=1
                )
                
                # Calculer la moyenne de buts par match
                player_goals_stats['Moy buts/match'] = player_goals_stats.apply(
                    lambda row: round(row['goals'] / row['matches_played'], 2) if row['matches_played'] > 0 else 0,
                    axis=1
                )
                
                # Renommer les colonnes
                player_goals_stats = player_goals_stats.rename(columns={
                    'player_name': 'Joueur',
                    'team_name': 'Équipe',
                    'goals': 'Buts',
                    'shots': 'Tirs',
                    'goals_7m': 'Buts 7m',
                    'matches_played': 'Matchs'
                })
                
                # Trier par buts (ordre décroissant)
                player_goals_stats = player_goals_stats.sort_values('Buts', ascending=False).reset_index(drop=True)
                player_goals_stats.insert(0, 'Rang', range(1, len(player_goals_stats) + 1))
                
                # Réorganiser les colonnes
                player_goals_stats = player_goals_stats[['Rang', 'Joueur', 'Équipe', 'Buts', 'Moy buts/match', 
                                                          '% Réussite', 'Tirs', 'Buts 7m', 'Matchs']]
                
                # Options de pagination
                st.markdown("#### Options d'affichage")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    rows_per_page = st.selectbox(
                        "Lignes par page",
                        options=[10, 25, 50, 100, len(player_goals_stats)],
                        index=2,
                        key="goals_pagination"
                    )
                
                with col2:
                    # Filtrer par équipe
                    teams_list = ['Toutes les équipes'] + sorted(player_goals_stats['Équipe'].unique().tolist())
                    selected_team = st.selectbox(
                        "Filtrer par équipe",
                        options=teams_list,
                        key="goals_team_filter"
                    )
                
                # Appliquer le filtre d'équipe
                if selected_team != 'Toutes les équipes':
                    filtered_stats = player_goals_stats[player_goals_stats['Équipe'] == selected_team].copy()
                    filtered_stats['Rang'] = range(1, len(filtered_stats) + 1)
                else:
                    filtered_stats = player_goals_stats
                
                # Afficher le nombre total de joueurs
                st.info(f"📊 Total de joueurs affichés : {len(filtered_stats)}")
                
                # Pagination
                if rows_per_page < len(filtered_stats):
                    total_pages = (len(filtered_stats) - 1) // rows_per_page + 1
                    page = st.number_input(
                        f"Page (1-{total_pages})",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        key="goals_page_number"
                    )
                    start_idx = (page - 1) * rows_per_page
                    end_idx = min(start_idx + rows_per_page, len(filtered_stats))
                    display_stats = filtered_stats.iloc[start_idx:end_idx]
                    
                    st.caption(f"Affichage des joueurs {start_idx + 1} à {end_idx} sur {len(filtered_stats)}")
                else:
                    display_stats = filtered_stats
                
                # Afficher le tableau
                st.dataframe(
                    display_stats,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistiques rapides
                st.markdown("---")
                st.markdown("### 📊 Statistiques globales")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    top_scorer = filtered_stats.iloc[0]
                    st.metric(
                        "Meilleur buteur",
                        top_scorer['Joueur'],
                        f"{int(top_scorer['Buts'])} buts"
                    )
                
                with col2:
                    avg_goals = filtered_stats['Buts'].mean()
                    st.metric(
                        "Moyenne de buts",
                        f"{avg_goals:.1f}"
                    )
                
                with col3:
                    total_goals = filtered_stats['Buts'].sum()
                    st.metric(
                        "Total de buts",
                        f"{int(total_goals)}"
                    )
                
                with col4:
                    avg_efficiency = filtered_stats['% Réussite'].mean()
                    st.metric(
                        "Efficacité moyenne",
                        f"{avg_efficiency:.1f}%"
                    )
                
                # Option de téléchargement
                st.download_button(
                    label="📥 Télécharger les statistiques complètes CSV",
                    data=filtered_stats.to_csv(index=False).encode('utf-8'),
                    file_name='stats_buteurs.csv',
                    mime='text/csv',
                )
            else:
                st.info("Aucune statistique de joueur disponible.")
        
        # Onglet 2: Classement des gardiens
        with tab2:
            st.markdown("### 🧤 Classement des gardiens")
            
            # Filtrer les joueurs (non officiels) pour identifier les gardiens
            # Un gardien est quelqu'un qui a au moins un arrêt dans sa carrière
            all_players = player_stats_df[player_stats_df['is_official'] == False].copy()
            
            # Identifier les gardiens (joueurs qui ont fait au moins 1 arrêt)
            goalkeeper_ids = all_players[all_players['saves'] > 0][['player_name', 'team_name']].drop_duplicates()
            
            if not goalkeeper_ids.empty:
                # Filtrer toutes les statistiques des gardiens (même les matchs sans arrêt)
                goalkeepers = all_players.merge(
                    goalkeeper_ids,
                    on=['player_name', 'team_name'],
                    how='inner'
                )
                
                # D'abord, calculer le nombre de matchs joués (tous les matchs, pas seulement ceux avec arrêts)
                matches_per_goalkeeper = goalkeepers.groupby(['player_name', 'team_name']).agg({
                    'match_id': 'nunique'
                }).reset_index()
                matches_per_goalkeeper = matches_per_goalkeeper.rename(columns={'match_id': 'matches_played'})
                
                # Grouper par joueur et équipe, sommer les statistiques
                goalkeeper_stats = goalkeepers.groupby(['player_name', 'team_name']).agg({
                    'saves': 'sum'
                }).reset_index()
                
                # Fusionner avec le nombre de matchs
                goalkeeper_stats = goalkeeper_stats.merge(
                    matches_per_goalkeeper,
                    on=['player_name', 'team_name'],
                    how='left'
                )
                
                # Calculer la moyenne d'arrêts par match
                goalkeeper_stats['Moy arrêts/match'] = goalkeeper_stats.apply(
                    lambda row: round(row['saves'] / row['matches_played'], 2) if row['matches_played'] > 0 else 0,
                    axis=1
                )
                
                # Renommer les colonnes
                goalkeeper_stats = goalkeeper_stats.rename(columns={
                    'player_name': 'Gardien',
                    'team_name': 'Équipe',
                    'saves': 'Arrêts',
                    'matches_played': 'Matchs'
                })
                
                # Trier par arrêts (ordre décroissant)
                goalkeeper_stats = goalkeeper_stats.sort_values('Arrêts', ascending=False).reset_index(drop=True)
                goalkeeper_stats.insert(0, 'Rang', range(1, len(goalkeeper_stats) + 1))
                
                # Réorganiser les colonnes
                goalkeeper_stats = goalkeeper_stats[['Rang', 'Gardien', 'Équipe', 'Arrêts', 'Moy arrêts/match', 'Matchs']]
                
                # Options de pagination
                st.markdown("#### Options d'affichage")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    rows_per_page_gk = st.selectbox(
                        "Lignes par page",
                        options=[10, 25, 50, 100, len(goalkeeper_stats)],
                        index=1,
                        key="goalkeeper_pagination"
                    )
                
                with col2:
                    # Filtrer par équipe
                    teams_list_gk = ['Toutes les équipes'] + sorted(goalkeeper_stats['Équipe'].unique().tolist())
                    selected_team_gk = st.selectbox(
                        "Filtrer par équipe",
                        options=teams_list_gk,
                        key="goalkeeper_team_filter"
                    )
                
                # Appliquer le filtre d'équipe
                if selected_team_gk != 'Toutes les équipes':
                    filtered_gk_stats = goalkeeper_stats[goalkeeper_stats['Équipe'] == selected_team_gk].copy()
                    filtered_gk_stats['Rang'] = range(1, len(filtered_gk_stats) + 1)
                else:
                    filtered_gk_stats = goalkeeper_stats
                
                # Afficher le nombre total de gardiens
                st.info(f"🧤 Total de gardiens affichés : {len(filtered_gk_stats)}")
                
                # Pagination
                if rows_per_page_gk < len(filtered_gk_stats):
                    total_pages_gk = (len(filtered_gk_stats) - 1) // rows_per_page_gk + 1
                    page_gk = st.number_input(
                        f"Page (1-{total_pages_gk})",
                        min_value=1,
                        max_value=total_pages_gk,
                        value=1,
                        key="goalkeeper_page_number"
                    )
                    start_idx_gk = (page_gk - 1) * rows_per_page_gk
                    end_idx_gk = min(start_idx_gk + rows_per_page_gk, len(filtered_gk_stats))
                    display_gk_stats = filtered_gk_stats.iloc[start_idx_gk:end_idx_gk]
                    
                    st.caption(f"Affichage des gardiens {start_idx_gk + 1} à {end_idx_gk} sur {len(filtered_gk_stats)}")
                else:
                    display_gk_stats = filtered_gk_stats
                
                # Afficher le tableau
                st.dataframe(
                    display_gk_stats,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistiques rapides
                st.markdown("---")
                st.markdown("### 📊 Statistiques globales des gardiens")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    top_goalkeeper = filtered_gk_stats.iloc[0]
                    st.metric(
                        "Meilleur gardien",
                        top_goalkeeper['Gardien'],
                        f"{int(top_goalkeeper['Arrêts'])} arrêts"
                    )
                
                with col2:
                    avg_saves = filtered_gk_stats['Arrêts'].mean()
                    st.metric(
                        "Moyenne d'arrêts",
                        f"{avg_saves:.1f}"
                    )
                
                with col3:
                    total_saves = filtered_gk_stats['Arrêts'].sum()
                    st.metric(
                        "Total d'arrêts",
                        f"{int(total_saves)}"
                    )
                
                # Option de téléchargement
                st.download_button(
                    label="📥 Télécharger les statistiques des gardiens CSV",
                    data=filtered_gk_stats.to_csv(index=False).encode('utf-8'),
                    file_name='stats_gardiens.csv',
                    mime='text/csv',
                )
            else:
                st.info("Aucune statistique de gardien disponible.")

except Exception as e:
    st.error(f"Erreur lors du chargement des statistiques : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    with st.expander("Détails de l'erreur"):
        st.error(str(e))
