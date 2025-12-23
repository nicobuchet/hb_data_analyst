"""
Tab: Buts 7m (7-meter goals)
"""
import streamlit as st
import pandas as pd
from .utils import calculate_team_matches


def render(matches_df: pd.DataFrame, teams_df: pd.DataFrame, player_stats_df: pd.DataFrame, stats_df: pd.DataFrame):
    """Render the 7-meter goals tab"""
    st.markdown("### 🎯 Classement des buts 7m")
    
    if not player_stats_df.empty:
        # Filtrer les joueurs avec des buts 7m
        players_with_7m = player_stats_df[
            (player_stats_df['is_official'] == False) & 
            (player_stats_df['goals_7m'] > 0)
        ].copy()
        
        if not players_with_7m.empty:
            # Grouper par équipe et sommer les buts 7m
            goals_7m_stats = players_with_7m.groupby('team_name').agg({
                'goals_7m': 'sum'
            }).reset_index()
            
            # Calculer le nombre de matchs par équipe
            matches_per_team = calculate_team_matches(matches_df, teams_df)
            
            # Fusionner avec les stats de buts 7m
            goals_7m_stats = goals_7m_stats.merge(matches_per_team, on='team_name', how='left')
            
            # Remplir les matchs manquants avec 0
            goals_7m_stats['matches'] = goals_7m_stats['matches'].fillna(0).astype(int)
            
            # Calculer la moyenne de buts 7m par match
            goals_7m_stats['Moy 7m'] = goals_7m_stats.apply(
                lambda row: round(row['goals_7m'] / row['matches'], 2) if row['matches'] > 0 else 0,
                axis=1
            )
            
            # Renommer les colonnes
            goals_7m_stats = goals_7m_stats.rename(columns={
                'team_name': 'Équipe',
                'goals_7m': 'Buts 7m',
                'matches': 'Matchs'
            })
            
            # Trier par buts 7m (ordre décroissant)
            goals_7m_stats = goals_7m_stats.sort_values('Buts 7m', ascending=False).reset_index(drop=True)
            goals_7m_stats.insert(0, 'Rang', range(1, len(goals_7m_stats) + 1))
            
            # Réorganiser les colonnes
            goals_7m_stats = goals_7m_stats[['Rang', 'Équipe', 'Buts 7m', 'Moy 7m', 'Matchs']]
            
            st.dataframe(
                goals_7m_stats,
                use_container_width=True,
                hide_index=True
            )
            
            # Statistiques rapides
            col1, col2, col3 = st.columns(3)
            with col1:
                best_7m = goals_7m_stats.iloc[0]
                st.metric(
                    "Meilleurs buteurs 7m",
                    best_7m['Équipe'],
                    f"{int(best_7m['Buts 7m'])} buts 7m"
                )
            with col2:
                avg_7m = goals_7m_stats['Buts 7m'].mean()
                st.metric(
                    "Moyenne de la ligue",
                    f"{avg_7m:.1f} buts 7m"
                )
            with col3:
                total_7m = goals_7m_stats['Buts 7m'].sum()
                st.metric(
                    "Total de buts 7m",
                    f"{int(total_7m)}"
                )
            
            st.download_button(
                label="📥 Télécharger les statistiques CSV",
                data=goals_7m_stats.to_csv(index=False).encode('utf-8'),
                file_name='stats_buts_7m.csv',
                mime='text/csv',
            )
        else:
            st.info("Aucun but 7m enregistré.")
    else:
        st.info("Aucune statistique de joueur disponible.")
