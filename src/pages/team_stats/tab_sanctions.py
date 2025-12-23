"""
Tab: Sanctions (Yellow/2min/Red/Blue cards)
"""
import streamlit as st
import pandas as pd
from .utils import calculate_team_matches


def render(matches_df: pd.DataFrame, teams_df: pd.DataFrame, player_stats_df: pd.DataFrame, stats_df: pd.DataFrame):
    """Render the sanctions tab"""
    st.markdown("### ⚠️ Classement des sanctions")
    
    if not player_stats_df.empty:
        # Filtrer les joueurs avec des sanctions
        players_with_sanctions = player_stats_df[
            (player_stats_df['is_official'] == False) & 
            (
                (player_stats_df['yellow_cards'] > 0) | 
                (player_stats_df['two_minutes'] > 0) | 
                (player_stats_df['red_cards'] > 0) | 
                (player_stats_df['blue_cards'] > 0)
            )
        ].copy()
        
        if not players_with_sanctions.empty:
            # Grouper par équipe et sommer toutes les sanctions
            sanctions_stats = players_with_sanctions.groupby('team_name').agg({
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
            
            # Calculer le nombre de matchs par équipe
            matches_per_team = calculate_team_matches(matches_df, teams_df)
            
            # Fusionner avec les stats de sanctions
            sanctions_stats = sanctions_stats.merge(matches_per_team, on='team_name', how='left')
            
            # Remplir les matchs manquants avec 0
            sanctions_stats['matches'] = sanctions_stats['matches'].fillna(0).astype(int)
            
            # Calculer la moyenne de sanctions par match
            sanctions_stats['Moy sanctions'] = sanctions_stats.apply(
                lambda row: round(row['total_sanctions'] / row['matches'], 2) if row['matches'] > 0 else 0,
                axis=1
            )
            
            # Renommer les colonnes
            sanctions_stats = sanctions_stats.rename(columns={
                'team_name': 'Équipe',
                'yellow_cards': 'Jaunes',
                'two_minutes': '2 min',
                'red_cards': 'Rouges',
                'blue_cards': 'Bleues',
                'total_sanctions': 'Total',
                'matches': 'Matchs'
            })
            
            # Trier par total de sanctions (ordre croissant - moins de sanctions = meilleur comportement)
            sanctions_stats = sanctions_stats.sort_values('Total', ascending=True).reset_index(drop=True)
            sanctions_stats.insert(0, 'Rang', range(1, len(sanctions_stats) + 1))
            
            # Réorganiser les colonnes
            sanctions_stats = sanctions_stats[
                ['Rang', 'Équipe', 'Total', 'Moy sanctions', 'Jaunes', '2 min', 'Rouges', 'Bleues', 'Matchs']
            ]
            
            st.dataframe(
                sanctions_stats,
                use_container_width=True,
                hide_index=True
            )
            
            # Statistiques rapides
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                best_discipline = sanctions_stats.iloc[0]
                st.metric(
                    "Équipe la plus disciplinée",
                    best_discipline['Équipe'],
                    f"{int(best_discipline['Total'])} sanctions"
                )
            with col2:
                avg_sanctions = sanctions_stats['Total'].mean()
                st.metric(
                    "Moyenne de la ligue",
                    f"{avg_sanctions:.1f} sanctions"
                )
            with col3:
                total_yellow = sanctions_stats['Jaunes'].sum()
                st.metric(
                    "Total cartons jaunes",
                    f"{int(total_yellow)}"
                )
            with col4:
                total_2min = sanctions_stats['2 min'].sum()
                st.metric(
                    "Total 2 minutes",
                    f"{int(total_2min)}"
                )
            
            st.download_button(
                label="📥 Télécharger les statistiques CSV",
                data=sanctions_stats.to_csv(index=False).encode('utf-8'),
                file_name='stats_sanctions.csv',
                mime='text/csv',
            )
        else:
            st.info("Aucune sanction enregistrée.")
    else:
        st.info("Aucune statistique de joueur disponible.")
