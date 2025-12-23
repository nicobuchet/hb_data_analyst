"""
Tab: Meilleures performances
"""
import streamlit as st
import pandas as pd


def render(player_stats_df: pd.DataFrame, matches_df: pd.DataFrame, teams_df: pd.DataFrame):
    """Render the best performances tab"""
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
