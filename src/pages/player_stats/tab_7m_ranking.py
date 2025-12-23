"""
Tab: Classement des 7m
"""
import streamlit as st
import pandas as pd


def render(player_stats_df: pd.DataFrame, matches_df: pd.DataFrame, teams_df: pd.DataFrame):
    """Render the 7m goals ranking tab"""
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
