"""
Tab: Meilleures performances gardiens
"""
import streamlit as st
import pandas as pd


def render(player_stats_df: pd.DataFrame, matches_df: pd.DataFrame, teams_df: pd.DataFrame):
    """Render the best goalkeeper performances tab"""
    st.markdown("### 🧤 Meilleures performances gardiens")
    
    # Filtrer les joueurs non officiels
    all_players = player_stats_df[player_stats_df['is_official'] == False].copy()
    
    if not all_players.empty and not matches_df.empty:
        # Filtrer les performances avec au moins 1 arrêt
        performances = all_players[all_players['saves'] > 0].copy()
        
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
            
            # Renommer les colonnes
            performances = performances.rename(columns={
                'player_name': 'Gardien',
                'team_name': 'Équipe',
                'saves': 'Arrêts'
            })
            
            # Sélectionner et réorganiser les colonnes
            performances_display = performances[['Gardien', 'Équipe', 'Arrêts', 'Match']].copy()
            
            # Trier par arrêts (ordre décroissant) et garder seulement les 100 meilleures
            performances_display = performances_display.sort_values('Arrêts', ascending=False).head(100).reset_index(drop=True)
            performances_display.insert(0, 'Rang', range(1, len(performances_display) + 1))
            
            # Afficher un message informatif
            st.info(f"🧤 Affichage des 100 meilleures performances gardien (sur {len(performances)} performances totales)")
            
            # Options de pagination
            st.markdown("#### Options d'affichage")
            col1, col2 = st.columns([1, 3])
            
            with col1:
                rows_per_page_perf = st.selectbox(
                    "Lignes par page",
                    options=[10, 25, 50, 100, len(performances_display)],
                    index=2,
                    key="gk_performance_pagination"
                )
            
            with col2:
                # Filtrer par équipe
                teams_list_perf = ['Toutes les équipes'] + sorted(performances_display['Équipe'].unique().tolist())
                selected_team_perf = st.selectbox(
                    "Filtrer par équipe",
                    options=teams_list_perf,
                    key="gk_performance_team_filter"
                )
            
            # Appliquer le filtre d'équipe
            if selected_team_perf != 'Toutes les équipes':
                filtered_perf = performances_display[performances_display['Équipe'] == selected_team_perf].copy()
                filtered_perf['Rang'] = range(1, len(filtered_perf) + 1)
            else:
                filtered_perf = performances_display
            
            # Pagination
            if rows_per_page_perf < len(filtered_perf):
                total_pages = (len(filtered_perf) - 1) // rows_per_page_perf + 1
                page = st.number_input(
                    f"Page (1-{total_pages})",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    key="gk_performance_page"
                )
                
                start_idx = (page - 1) * rows_per_page_perf
                end_idx = start_idx + rows_per_page_perf
                display_data = filtered_perf.iloc[start_idx:end_idx]
                
                st.info(f"Affichage des performances {start_idx + 1} à {min(end_idx, len(filtered_perf))} sur {len(filtered_perf)}")
            else:
                display_data = filtered_perf
            
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
                    "Gardien": st.column_config.TextColumn(
                        "Gardien",
                        help="Nom du gardien",
                        width="medium"
                    ),
                    "Équipe": st.column_config.TextColumn(
                        "Équipe",
                        help="Équipe",
                        width="medium"
                    ),
                    "Arrêts": st.column_config.NumberColumn(
                        "Arrêts",
                        help="Nombre d'arrêts dans le match",
                        width="small"
                    ),
                    "Match": st.column_config.TextColumn(
                        "Match",
                        help="Informations du match",
                        width="large"
                    )
                }
            )
            
            # Statistiques rapides
            st.markdown("#### 📊 Statistiques rapides")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                best_perf = filtered_perf.iloc[0]
                st.metric(
                    "Meilleure performance",
                    f"{best_perf['Gardien']}",
                    f"{int(best_perf['Arrêts'])} arrêts"
                )
            
            with col2:
                avg_saves = filtered_perf['Arrêts'].mean()
                st.metric(
                    "Moyenne top 100",
                    f"{avg_saves:.1f} arrêts"
                )
            
            with col3:
                total_performances = len(filtered_perf)
                st.metric(
                    "Performances affichées",
                    f"{total_performances}"
                )
            
            with col4:
                unique_goalkeepers = filtered_perf['Gardien'].nunique()
                st.metric(
                    "Gardiens différents",
                    f"{unique_goalkeepers}"
                )
            
            # Bouton de téléchargement
            st.download_button(
                label="📥 Télécharger les statistiques CSV",
                data=filtered_perf.to_csv(index=False).encode('utf-8'),
                file_name='meilleures_performances_gardiens.csv',
                mime='text/csv',
            )
        else:
            st.info("Aucune performance de gardien enregistrée.")
    else:
        st.info("Aucune donnée disponible.")
