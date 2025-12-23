"""
Tab: Classement des gardiens
"""
import streamlit as st
import pandas as pd


def render(player_stats_df: pd.DataFrame, matches_df: pd.DataFrame, teams_df: pd.DataFrame):
    """Render the goalkeepers ranking tab"""
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
