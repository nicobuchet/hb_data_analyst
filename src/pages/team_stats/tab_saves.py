"""
Tab: Arrêts (Saves)
"""
import streamlit as st
import pandas as pd
from .utils import calculate_team_matches


def render(matches_df: pd.DataFrame, teams_df: pd.DataFrame, player_stats_df: pd.DataFrame, stats_df: pd.DataFrame):
    """Render the saves tab"""
    st.markdown("### 🧤 Classement des arrêts")
    
    if not player_stats_df.empty:
        # Filtrer les gardiens (joueurs avec arrêts > 0)
        goalkeepers = player_stats_df[
            (player_stats_df['is_official'] == False) & 
            (player_stats_df['saves'] > 0)
        ].copy()
        
        if not goalkeepers.empty:
            # Grouper par équipe et sommer les arrêts
            saves_stats = goalkeepers.groupby('team_name').agg({
                'saves': 'sum'
            }).reset_index()
            
            # Calculer le nombre de matchs par équipe
            matches_per_team = calculate_team_matches(matches_df, teams_df)
            
            # Fusionner avec les stats d'arrêts
            saves_stats = saves_stats.merge(matches_per_team, on='team_name', how='left')
            
            # Remplir les matchs manquants avec 0
            saves_stats['matches'] = saves_stats['matches'].fillna(0).astype(int)
            
            # Calculer la moyenne d'arrêts par match
            saves_stats['Moy arrêts'] = saves_stats.apply(
                lambda row: round(row['saves'] / row['matches'], 2) if row['matches'] > 0 else 0,
                axis=1
            )
            
            # Renommer les colonnes
            saves_stats = saves_stats.rename(columns={
                'team_name': 'Équipe',
                'saves': 'Arrêts',
                'matches': 'Matchs'
            })
            
            # Trier par arrêts (ordre décroissant)
            saves_stats = saves_stats.sort_values('Arrêts', ascending=False).reset_index(drop=True)
            saves_stats.insert(0, 'Rang', range(1, len(saves_stats) + 1))
            
            # Réorganiser les colonnes
            saves_stats = saves_stats[['Rang', 'Équipe', 'Arrêts', 'Moy arrêts', 'Matchs']]
            
            st.dataframe(
                saves_stats,
                use_container_width=True,
                hide_index=True
            )
            
            # Statistiques rapides
            col1, col2, col3 = st.columns(3)
            with col1:
                best_saves = saves_stats.iloc[0]
                st.metric(
                    "Meilleurs gardiens",
                    best_saves['Équipe'],
                    f"{int(best_saves['Arrêts'])} arrêts"
                )
            with col2:
                avg_saves = saves_stats['Arrêts'].mean()
                st.metric(
                    "Moyenne de la ligue",
                    f"{avg_saves:.1f} arrêts"
                )
            with col3:
                total_saves = saves_stats['Arrêts'].sum()
                st.metric(
                    "Total d'arrêts",
                    f"{int(total_saves)}"
                )
            
            st.download_button(
                label="📥 Télécharger les statistiques CSV",
                data=saves_stats.to_csv(index=False).encode('utf-8'),
                file_name='stats_arrets.csv',
                mime='text/csv',
            )
        else:
            st.info("Aucune statistique de gardien disponible.")
    else:
        st.info("Aucune statistique de joueur disponible.")
