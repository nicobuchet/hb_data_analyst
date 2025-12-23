"""
Tab: Meilleures performances 7m
"""
import streamlit as st
import pandas as pd


def render(player_stats_df: pd.DataFrame, matches_df: pd.DataFrame, teams_df: pd.DataFrame):
    """Render the best 7m performances tab"""
    st.markdown("### 🎯 Meilleures performances 7m")
    
    # Filtrer les joueurs de champ (non officiels)
    field_players_7m = player_stats_df[player_stats_df['is_official'] == False].copy()
    
    if not field_players_7m.empty and not matches_df.empty:
        # Filtrer les performances avec au moins 1 but 7m
        performances_7m = field_players_7m[field_players_7m['goals_7m'] > 0].copy()
        
        if not performances_7m.empty:
            # Fusionner avec les informations des matchs
            performances_7m = performances_7m.merge(
                matches_df[['id', 'home_team_id', 'away_team_id', 'match_date', 
                            'final_score_home', 'final_score_away']],
                left_on='match_id',
                right_on='id',
                how='left'
            )
            
            # Ajouter les noms des équipes
            performances_7m = performances_7m.merge(
                teams_df[['id', 'name']],
                left_on='home_team_id',
                right_on='id',
                how='left',
                suffixes=('', '_home')
            ).rename(columns={'name': 'home_team_name'})
            
            performances_7m = performances_7m.merge(
                teams_df[['id', 'name']],
                left_on='away_team_id',
                right_on='id',
                how='left',
                suffixes=('', '_away')
            ).rename(columns={'name': 'away_team_name'})
            
            # Créer la colonne "Match" avec le format demandé
            def format_match_info_7m(row):
                if pd.notna(row.get('home_team_name')) and pd.notna(row.get('away_team_name')):
                    # Construire la chaîne du match sur deux lignes
                    match_line = f"{row['home_team_name']} {int(row['final_score_home'])} - {int(row['final_score_away'])} {row['away_team_name']}"
                    date_line = pd.to_datetime(row['match_date']).strftime('%d/%m/%Y')
                    return f"{match_line}\n({date_line})"
                return "N/A"
            
            performances_7m['Match'] = performances_7m.apply(format_match_info_7m, axis=1)
            
            # Renommer les colonnes
            performances_7m = performances_7m.rename(columns={
                'player_name': 'Joueur',
                'team_name': 'Équipe',
                'goals_7m': 'Buts 7m'
            })
            
            # Sélectionner et réorganiser les colonnes
            performances_7m_display = performances_7m[['Joueur', 'Équipe', 'Buts 7m', 'Match']].copy()
            
            # Trier par buts 7m (ordre décroissant) et garder seulement les 100 meilleures
            performances_7m_display = performances_7m_display.sort_values('Buts 7m', ascending=False).head(100).reset_index(drop=True)
            performances_7m_display.insert(0, 'Rang', range(1, len(performances_7m_display) + 1))
            
            # Afficher un message informatif
            st.info(f"🎯 Affichage des 100 meilleures performances 7m (sur {len(performances_7m)} performances totales)")
            
            # Options de pagination
            st.markdown("#### Options d'affichage")
            col1, col2 = st.columns([1, 3])
            
            with col1:
                rows_per_page_perf_7m = st.selectbox(
                    "Lignes par page",
                    options=[10, 25, 50, 100, len(performances_7m_display)],
                    index=2,
                    key="performance_7m_pagination"
                )
            
            with col2:
                # Filtrer par équipe
                teams_list_perf_7m = ['Toutes les équipes'] + sorted(performances_7m_display['Équipe'].unique().tolist())
                selected_team_perf_7m = st.selectbox(
                    "Filtrer par équipe",
                    options=teams_list_perf_7m,
                    key="performance_7m_team_filter"
                )
            
            # Appliquer le filtre d'équipe
            if selected_team_perf_7m != 'Toutes les équipes':
                filtered_perf_7m_stats = performances_7m_display[performances_7m_display['Équipe'] == selected_team_perf_7m].copy()
                filtered_perf_7m_stats['Rang'] = range(1, len(filtered_perf_7m_stats) + 1)
            else:
                filtered_perf_7m_stats = performances_7m_display
            
            # Pagination
            if rows_per_page_perf_7m < len(filtered_perf_7m_stats):
                total_pages_perf_7m = (len(filtered_perf_7m_stats) - 1) // rows_per_page_perf_7m + 1
                page_perf_7m = st.number_input(
                    f"Page (1-{total_pages_perf_7m})",
                    min_value=1,
                    max_value=total_pages_perf_7m,
                    value=1,
                    key="performance_7m_page_number"
                )
                start_idx_perf_7m = (page_perf_7m - 1) * rows_per_page_perf_7m
                end_idx_perf_7m = min(start_idx_perf_7m + rows_per_page_perf_7m, len(filtered_perf_7m_stats))
                display_perf_7m_stats = filtered_perf_7m_stats.iloc[start_idx_perf_7m:end_idx_perf_7m]
                
                st.caption(f"Affichage des performances {start_idx_perf_7m + 1} à {end_idx_perf_7m} sur {len(filtered_perf_7m_stats)}")
            else:
                display_perf_7m_stats = filtered_perf_7m_stats
            
            # Afficher le tableau
            st.dataframe(
                display_perf_7m_stats,
                use_container_width=True,
                hide_index=True
            )
            
            # Statistiques rapides
            st.markdown("---")
            st.markdown("### 📊 Statistiques des meilleures performances 7m")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                best_perf_7m = filtered_perf_7m_stats.iloc[0]
                st.metric(
                    "Meilleure performance",
                    best_perf_7m['Joueur'],
                    f"{int(best_perf_7m['Buts 7m'])} buts 7m"
                )
            
            with col2:
                avg_7m_per_match = filtered_perf_7m_stats['Buts 7m'].mean()
                st.metric(
                    "Moyenne de 7m/match",
                    f"{avg_7m_per_match:.1f}"
                )
            
            with col3:
                total_7m_perfs = filtered_perf_7m_stats['Buts 7m'].sum()
                st.metric(
                    "Total de buts 7m",
                    f"{int(total_7m_perfs)}"
                )
            
            with col4:
                perfs_3plus = len(filtered_perf_7m_stats[filtered_perf_7m_stats['Buts 7m'] >= 3])
                st.metric(
                    "Performances 3+ buts 7m",
                    f"{perfs_3plus}"
                )
            
            # Option de téléchargement
            st.download_button(
                label="📥 Télécharger les performances 7m CSV",
                data=filtered_perf_7m_stats.to_csv(index=False).encode('utf-8'),
                file_name='meilleures_performances_7m.csv',
                mime='text/csv',
            )
        else:
            st.info("Aucune performance 7m disponible.")
    else:
        st.info("Aucune donnée disponible pour afficher les performances 7m.")
