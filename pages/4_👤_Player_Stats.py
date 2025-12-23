"""
Page Statistiques de joueurs - Statistiques individuelles des joueurs
"""
import streamlit as st
import pandas as pd
from src.database import get_player_stats, get_matches, get_teams

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
        tab1, tab2, tab3, tab4 = st.tabs([
            "⚽ Classement des buteurs", 
            "🧤 Classement des gardiens", 
            "🎯 Classement des 7m",
            "🌟 Meilleures performances"
        ])
        
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
                    'shots': 'sum'
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
                    'matches_played': 'Matchs'
                })
                
                # Trier par buts (ordre décroissant)
                player_goals_stats = player_goals_stats.sort_values('Buts', ascending=False).reset_index(drop=True)
                player_goals_stats.insert(0, 'Rang', range(1, len(player_goals_stats) + 1))
                
                # Réorganiser les colonnes
                player_goals_stats = player_goals_stats[['Rang', 'Joueur', 'Équipe', 'Buts', 'Moy buts/match', 
                                                          '% Réussite', 'Tirs', 'Matchs']]
                
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
        
        # Onglet 3: Classement des 7m
        with tab3:
            st.markdown("### 🎯 Classement des buts sur 7 mètres")
            
            # Filtrer les joueurs (non officiels)
            players_7m = player_stats_df[player_stats_df['is_official'] == False].copy()
            
            if not players_7m.empty:
                # D'abord, calculer le nombre de matchs joués par joueur
                matches_per_player_7m = players_7m.groupby(['player_name', 'team_name']).agg({
                    'match_id': 'nunique'
                }).reset_index()
                matches_per_player_7m = matches_per_player_7m.rename(columns={'match_id': 'matches_played'})
                
                # Grouper par joueur et équipe, sommer les statistiques
                player_7m_stats = players_7m.groupby(['player_name', 'team_name']).agg({
                    'goals_7m': 'sum'
                }).reset_index()
                
                # Fusionner avec le nombre de matchs
                player_7m_stats = player_7m_stats.merge(
                    matches_per_player_7m,
                    on=['player_name', 'team_name'],
                    how='left'
                )
                
                # Filtrer les joueurs avec au moins 1 but 7m
                player_7m_stats = player_7m_stats[player_7m_stats['goals_7m'] > 0].copy()
                
                # Calculer la moyenne de buts 7m par match
                player_7m_stats['Moy 7m/match'] = player_7m_stats.apply(
                    lambda row: round(row['goals_7m'] / row['matches_played'], 2) if row['matches_played'] > 0 else 0,
                    axis=1
                )
                
                # Renommer les colonnes
                player_7m_stats = player_7m_stats.rename(columns={
                    'player_name': 'Joueur',
                    'team_name': 'Équipe',
                    'goals_7m': 'Buts 7m',
                    'matches_played': 'Matchs'
                })
                
                # Trier par buts 7m (ordre décroissant)
                player_7m_stats = player_7m_stats.sort_values('Buts 7m', ascending=False).reset_index(drop=True)
                player_7m_stats.insert(0, 'Rang', range(1, len(player_7m_stats) + 1))
                
                # Réorganiser les colonnes
                player_7m_stats = player_7m_stats[['Rang', 'Joueur', 'Équipe', 'Buts 7m', 'Moy 7m/match', 'Matchs']]
                
                # Options de pagination
                st.markdown("#### Options d'affichage")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    rows_per_page_7m = st.selectbox(
                        "Lignes par page",
                        options=[10, 25, 50, 100, len(player_7m_stats)],
                        index=1,
                        key="7m_pagination"
                    )
                
                with col2:
                    # Filtrer par équipe
                    teams_list_7m = ['Toutes les équipes'] + sorted(player_7m_stats['Équipe'].unique().tolist())
                    selected_team_7m = st.selectbox(
                        "Filtrer par équipe",
                        options=teams_list_7m,
                        key="7m_team_filter"
                    )
                
                # Appliquer le filtre d'équipe
                if selected_team_7m != 'Toutes les équipes':
                    filtered_7m_stats = player_7m_stats[player_7m_stats['Équipe'] == selected_team_7m].copy()
                    filtered_7m_stats['Rang'] = range(1, len(filtered_7m_stats) + 1)
                else:
                    filtered_7m_stats = player_7m_stats
                
                # Afficher le nombre total de joueurs
                st.info(f"🎯 Total de joueurs affichés : {len(filtered_7m_stats)}")
                
                # Pagination
                if rows_per_page_7m < len(filtered_7m_stats):
                    total_pages_7m = (len(filtered_7m_stats) - 1) // rows_per_page_7m + 1
                    page_7m = st.number_input(
                        f"Page (1-{total_pages_7m})",
                        min_value=1,
                        max_value=total_pages_7m,
                        value=1,
                        key="7m_page_number"
                    )
                    start_idx_7m = (page_7m - 1) * rows_per_page_7m
                    end_idx_7m = min(start_idx_7m + rows_per_page_7m, len(filtered_7m_stats))
                    display_7m_stats = filtered_7m_stats.iloc[start_idx_7m:end_idx_7m]
                    
                    st.caption(f"Affichage des joueurs {start_idx_7m + 1} à {end_idx_7m} sur {len(filtered_7m_stats)}")
                else:
                    display_7m_stats = filtered_7m_stats
                
                # Afficher le tableau
                st.dataframe(
                    display_7m_stats,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistiques rapides
                st.markdown("---")
                st.markdown("### 📊 Statistiques globales des 7m")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    top_7m_scorer = filtered_7m_stats.iloc[0]
                    st.metric(
                        "Meilleur tireur 7m",
                        top_7m_scorer['Joueur'],
                        f"{int(top_7m_scorer['Buts 7m'])} buts"
                    )
                
                with col2:
                    avg_7m = filtered_7m_stats['Buts 7m'].mean()
                    st.metric(
                        "Moyenne de buts 7m",
                        f"{avg_7m:.1f}"
                    )
                
                with col3:
                    total_7m = filtered_7m_stats['Buts 7m'].sum()
                    st.metric(
                        "Total de buts 7m",
                        f"{int(total_7m)}"
                    )
                
                # Option de téléchargement
                st.download_button(
                    label="📥 Télécharger les statistiques des 7m CSV",
                    data=filtered_7m_stats.to_csv(index=False).encode('utf-8'),
                    file_name='stats_7m.csv',
                    mime='text/csv',
                )
            else:
                st.info("Aucune statistique de 7m disponible.")
        
        # Onglet 4: Meilleures performances individuelles par match
        with tab4:
            st.markdown("### 🌟 Meilleures performances individuelles")
            
            # Filtrer les joueurs de champ (non officiels, non gardiens)
            field_players = player_stats_df[player_stats_df['is_official'] == False].copy()
            
            if not field_players.empty and not matches_df.empty:
                # Filtrer les performances avec au moins 1 but
                performances = field_players[field_players['goals'] > 0].copy()
                
                if not performances.empty:
                    # Fusionner avec les informations des matchs
                    performances = performances.merge(
                        matches_df[['id', 'home_team_id', 'away_team_id', 'match_date', 
                                    'final_score_home', 'final_score_away']],
                        left_on='match_id',
                        right_on='id',
                        how='left'
                    )
                    
                    # Ajouter les noms des équipes
                    performances = performances.merge(
                        teams_df[['id', 'name']],
                        left_on='home_team_id',
                        right_on='id',
                        how='left',
                        suffixes=('', '_home')
                    ).rename(columns={'name': 'home_team_name'})
                    
                    performances = performances.merge(
                        teams_df[['id', 'name']],
                        left_on='away_team_id',
                        right_on='id',
                        how='left',
                        suffixes=('', '_away')
                    ).rename(columns={'name': 'away_team_name'})
                    
                    # Créer la colonne "Match" avec le format demandé
                    def format_match_info(row):
                        if pd.notna(row.get('home_team_name')) and pd.notna(row.get('away_team_name')):
                            # Construire la chaîne du match sur deux lignes
                            match_line = f"{row['home_team_name']} {int(row['final_score_home'])} - {int(row['final_score_away'])} {row['away_team_name']}"
                            date_line = pd.to_datetime(row['match_date']).strftime('%d/%m/%Y')
                            return f"{match_line}\n({date_line})"
                        return "N/A"
                    
                    performances['Match'] = performances.apply(format_match_info, axis=1)
                    
                    # Calculer l'efficacité
                    performances['Efficacité'] = performances.apply(
                        lambda row: round(row['goals'] / row['shots'] * 100, 2) if row['shots'] > 0 else 0,
                        axis=1
                    )
                    
                    # Renommer les colonnes
                    performances = performances.rename(columns={
                        'player_name': 'Joueur',
                        'team_name': 'Équipe',
                        'goals': 'Buts',
                        'shots': 'Tirs'
                    })
                    
                    # Sélectionner et réorganiser les colonnes
                    performances_display = performances[['Joueur', 'Équipe', 'Buts', 'Tirs', 
                                                          'Efficacité', 'Match']].copy()
                    
                    # Trier par buts (ordre décroissant) et garder seulement les 100 meilleures
                    performances_display = performances_display.sort_values('Buts', ascending=False).head(100).reset_index(drop=True)
                    performances_display.insert(0, 'Rang', range(1, len(performances_display) + 1))
                    
                    # Afficher un message informatif
                    st.info(f"🌟 Affichage des 100 meilleures performances (sur {len(performances)} performances totales)")
                    
                    # Options de pagination
                    st.markdown("#### Options d'affichage")
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        rows_per_page_perf = st.selectbox(
                            "Lignes par page",
                            options=[10, 25, 50, 100, len(performances_display)],
                            index=2,
                            key="performance_pagination"
                        )
                    
                    with col2:
                        # Filtrer par équipe
                        teams_list_perf = ['Toutes les équipes'] + sorted(performances_display['Équipe'].unique().tolist())
                        selected_team_perf = st.selectbox(
                            "Filtrer par équipe",
                            options=teams_list_perf,
                            key="performance_team_filter"
                        )
                    
                    # Appliquer le filtre d'équipe
                    if selected_team_perf != 'Toutes les équipes':
                        filtered_perf_stats = performances_display[performances_display['Équipe'] == selected_team_perf].copy()
                        filtered_perf_stats['Rang'] = range(1, len(filtered_perf_stats) + 1)
                    else:
                        filtered_perf_stats = performances_display
                    
                    # Pagination
                    if rows_per_page_perf < len(filtered_perf_stats):
                        total_pages_perf = (len(filtered_perf_stats) - 1) // rows_per_page_perf + 1
                        page_perf = st.number_input(
                            f"Page (1-{total_pages_perf})",
                            min_value=1,
                            max_value=total_pages_perf,
                            value=1,
                            key="performance_page_number"
                        )
                        start_idx_perf = (page_perf - 1) * rows_per_page_perf
                        end_idx_perf = min(start_idx_perf + rows_per_page_perf, len(filtered_perf_stats))
                        display_perf_stats = filtered_perf_stats.iloc[start_idx_perf:end_idx_perf]
                        
                        st.caption(f"Affichage des performances {start_idx_perf + 1} à {end_idx_perf} sur {len(filtered_perf_stats)}")
                    else:
                        display_perf_stats = filtered_perf_stats
                    
                    # Afficher le tableau
                    st.dataframe(
                        display_perf_stats,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Statistiques rapides
                    st.markdown("---")
                    st.markdown("### 📊 Statistiques des meilleures performances")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        best_perf = filtered_perf_stats.iloc[0]
                        st.metric(
                            "Meilleure performance",
                            best_perf['Joueur'],
                            f"{int(best_perf['Buts'])} buts"
                        )
                    
                    with col2:
                        avg_goals_per_match = filtered_perf_stats['Buts'].mean()
                        st.metric(
                            "Moyenne de buts/match",
                            f"{avg_goals_per_match:.1f}"
                        )
                    
                    with col3:
                        avg_efficiency = filtered_perf_stats['Efficacité'].mean()
                        st.metric(
                            "Efficacité moyenne",
                            f"{avg_efficiency:.1f}%"
                        )
                    
                    with col4:
                        perfs_5plus = len(filtered_perf_stats[filtered_perf_stats['Buts'] >= 5])
                        st.metric(
                            "Performances 5+ buts",
                            f"{perfs_5plus}"
                        )
                    
                    # Option de téléchargement
                    st.download_button(
                        label="📥 Télécharger les performances CSV",
                        data=filtered_perf_stats.to_csv(index=False).encode('utf-8'),
                        file_name='meilleures_performances.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("Aucune performance disponible.")
            else:
                st.info("Aucune donnée disponible pour afficher les performances.")

except Exception as e:
    st.error(f"Erreur lors du chargement des statistiques : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    with st.expander("Détails de l'erreur"):
        st.error(str(e))
