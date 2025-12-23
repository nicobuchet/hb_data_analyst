"""
Tab: Classement des sanctions
"""
import streamlit as st
import pandas as pd


def render(player_stats_df: pd.DataFrame, matches_df: pd.DataFrame, teams_df: pd.DataFrame):
    """Render the sanctions ranking tab"""
    st.markdown("### ⚠️ Classement des sanctions")
    
    # Filtrer les joueurs (non officiels)
    all_players = player_stats_df[player_stats_df['is_official'] == False].copy()
    
    # Filtrer les joueurs qui ont au moins une sanction
    players_with_sanctions = all_players[
        (all_players['yellow_cards'] > 0) | 
        (all_players['two_minutes'] > 0) | 
        (all_players['red_cards'] > 0) | 
        (all_players['blue_cards'] > 0)
    ]
    
    if not players_with_sanctions.empty:
        # D'abord, calculer le nombre de matchs joués par joueur
        matches_per_player = all_players.merge(
            players_with_sanctions[['player_name', 'team_name']].drop_duplicates(),
            on=['player_name', 'team_name'],
            how='inner'
        ).groupby(['player_name', 'team_name']).agg({
            'match_id': 'nunique'
        }).reset_index()
        matches_per_player = matches_per_player.rename(columns={'match_id': 'matches_played'})
        
        # Grouper par joueur et équipe, sommer toutes les sanctions
        sanctions_stats = players_with_sanctions.groupby(['player_name', 'team_name']).agg({
            'yellow_cards': 'sum',
            'two_minutes': 'sum',
            'red_cards': 'sum',
            'blue_cards': 'sum'
        }).reset_index()
        
        # Calculer le total des sanctions
        sanctions_stats['total_sanctions'] = (
            sanctions_stats['yellow_cards'] + 
            sanctions_stats['two_minutes'] + 
            sanctions_stats['red_cards'] + 
            sanctions_stats['blue_cards']
        )
        
        # Fusionner avec le nombre de matchs
        sanctions_stats = sanctions_stats.merge(
            matches_per_player,
            on=['player_name', 'team_name'],
            how='left'
        )
        
        # Calculer la moyenne de sanctions par match
        sanctions_stats['Moy sanctions/match'] = sanctions_stats.apply(
            lambda row: round(row['total_sanctions'] / row['matches_played'], 2) if row['matches_played'] > 0 else 0,
            axis=1
        )
        
        # Renommer les colonnes
        sanctions_stats = sanctions_stats.rename(columns={
            'player_name': 'Joueur',
            'team_name': 'Équipe',
            'yellow_cards': 'Jaunes',
            'two_minutes': '2 min',
            'red_cards': 'Rouges',
            'blue_cards': 'Bleues',
            'total_sanctions': 'Total',
            'matches_played': 'Matchs'
        })
        
        # Trier par total de sanctions (ordre décroissant - plus de sanctions = moins discipliné)
        sanctions_stats = sanctions_stats.sort_values('Total', ascending=False).reset_index(drop=True)
        sanctions_stats.insert(0, 'Rang', range(1, len(sanctions_stats) + 1))
        
        # Réorganiser les colonnes
        sanctions_stats = sanctions_stats[
            ['Rang', 'Joueur', 'Équipe', 'Total', 'Moy sanctions/match', 'Jaunes', '2 min', 'Rouges', 'Bleues', 'Matchs']
        ]
        
        # Options de pagination
        st.markdown("#### Options d'affichage")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            rows_per_page_sanctions = st.selectbox(
                "Lignes par page",
                options=[10, 25, 50, 100, len(sanctions_stats)],
                index=1,
                key="sanctions_pagination"
            )
        
        with col2:
            # Filtrer par équipe
            teams_list_sanctions = ['Toutes les équipes'] + sorted(sanctions_stats['Équipe'].unique().tolist())
            selected_team_sanctions = st.selectbox(
                "Filtrer par équipe",
                options=teams_list_sanctions,
                key="sanctions_team_filter"
            )
        
        # Appliquer le filtre d'équipe
        if selected_team_sanctions != 'Toutes les équipes':
            filtered_sanctions = sanctions_stats[sanctions_stats['Équipe'] == selected_team_sanctions].copy()
            filtered_sanctions['Rang'] = range(1, len(filtered_sanctions) + 1)
        else:
            filtered_sanctions = sanctions_stats
        
        # Afficher le nombre total de joueurs
        st.info(f"⚠️ Total de joueurs avec sanctions : {len(filtered_sanctions)}")
        
        # Pagination
        if rows_per_page_sanctions < len(filtered_sanctions):
            total_pages_sanctions = (len(filtered_sanctions) - 1) // rows_per_page_sanctions + 1
            page_sanctions = st.number_input(
                f"Page (1-{total_pages_sanctions})",
                min_value=1,
                max_value=total_pages_sanctions,
                value=1,
                key="sanctions_page"
            )
            
            start_idx = (page_sanctions - 1) * rows_per_page_sanctions
            end_idx = start_idx + rows_per_page_sanctions
            display_data = filtered_sanctions.iloc[start_idx:end_idx]
            
            st.info(f"Affichage des joueurs {start_idx + 1} à {min(end_idx, len(filtered_sanctions))} sur {len(filtered_sanctions)}")
        else:
            display_data = filtered_sanctions
        
        # Afficher le tableau
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rang": st.column_config.NumberColumn(
                    "Rang",
                    help="Classement",
                    width="small"
                ),
                "Joueur": st.column_config.TextColumn(
                    "Joueur",
                    help="Nom du joueur",
                    width="medium"
                ),
                "Équipe": st.column_config.TextColumn(
                    "Équipe",
                    help="Équipe",
                    width="medium"
                ),
                "Total": st.column_config.NumberColumn(
                    "Total",
                    help="Total de toutes les sanctions",
                    width="small"
                ),
                "Moy sanctions/match": st.column_config.NumberColumn(
                    "Moy/match",
                    help="Moyenne de sanctions par match",
                    width="small",
                    format="%.2f"
                ),
                "Jaunes": st.column_config.NumberColumn(
                    "Jaunes",
                    help="Cartons jaunes",
                    width="small"
                ),
                "2 min": st.column_config.NumberColumn(
                    "2 min",
                    help="Suspensions 2 minutes",
                    width="small"
                ),
                "Rouges": st.column_config.NumberColumn(
                    "Rouges",
                    help="Cartons rouges",
                    width="small"
                ),
                "Bleues": st.column_config.NumberColumn(
                    "Bleues",
                    help="Cartons bleus",
                    width="small"
                ),
                "Matchs": st.column_config.NumberColumn(
                    "Matchs",
                    help="Nombre de matchs joués",
                    width="small"
                )
            }
        )
        
        # Statistiques rapides
        st.markdown("#### 📊 Statistiques rapides")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            most_sanctioned = filtered_sanctions.iloc[0]
            st.metric(
                "Joueur le moins discipliné",
                f"{most_sanctioned['Joueur']}",
                f"{int(most_sanctioned['Total'])} sanctions"
            )
        
        with col2:
            avg_sanctions = filtered_sanctions['Total'].mean()
            st.metric(
                "Moyenne de sanctions",
                f"{avg_sanctions:.1f}"
            )
        
        with col3:
            total_yellow = filtered_sanctions['Jaunes'].sum()
            st.metric(
                "Total cartons jaunes",
                f"{int(total_yellow)}"
            )
        
        with col4:
            total_2min = filtered_sanctions['2 min'].sum()
            st.metric(
                "Total 2 minutes",
                f"{int(total_2min)}"
            )
        
        # Statistiques supplémentaires
        st.markdown("#### 🔍 Statistiques détaillées")
        col5, col6, col7 = st.columns(3)
        
        with col5:
            total_red = filtered_sanctions['Rouges'].sum()
            st.metric(
                "Total cartons rouges",
                f"{int(total_red)}"
            )
        
        with col6:
            total_blue = filtered_sanctions['Bleues'].sum()
            st.metric(
                "Total cartons bleus",
                f"{int(total_blue)}"
            )
        
        with col7:
            total_all_sanctions = filtered_sanctions['Total'].sum()
            st.metric(
                "Total toutes sanctions",
                f"{int(total_all_sanctions)}"
            )
        
        # Bouton de téléchargement
        st.download_button(
            label="📥 Télécharger les statistiques CSV",
            data=filtered_sanctions.to_csv(index=False).encode('utf-8'),
            file_name='classement_sanctions.csv',
            mime='text/csv',
        )
    else:
        st.info("Aucune sanction enregistrée.")
