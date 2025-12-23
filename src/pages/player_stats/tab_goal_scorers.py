"""
Tab: Classement des buteurs
"""
import streamlit as st
import pandas as pd


def render(player_stats_df: pd.DataFrame, matches_df: pd.DataFrame, teams_df: pd.DataFrame):
    """Render the goal scorers ranking tab"""
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
