"""
Tab: Pourcentage de réussite
"""
import streamlit as st
import pandas as pd


def render(matches_df: pd.DataFrame, teams_df: pd.DataFrame, player_stats_df: pd.DataFrame, stats_df: pd.DataFrame):
    """Render the shooting percentage tab"""
    st.markdown("### 🎯 Classement du pourcentage de réussite")
    
    if not player_stats_df.empty:
        # Filtrer les joueurs (non officiels)
        players = player_stats_df[player_stats_df['is_official'] == False].copy()
        
        if not players.empty:
            # Grouper par équipe, match et joueur pour éviter les doublons, puis sommer par équipe
            unique_stats = players.groupby(['match_id', 'team_name', 'player_id']).agg({
                'goals': 'max',  # Utiliser max au cas où il y aurait des doublons
                'shots': 'max'
            }).reset_index()
            
            # Ensuite, grouper par équipe et sommer tous les matchs
            shooting_stats = unique_stats.groupby('team_name').agg({
                'goals': 'sum',
                'shots': 'sum'
            }).reset_index()
            
            # Filtrer les équipes avec au moins 1 tir
            shooting_stats = shooting_stats[shooting_stats['shots'] > 0].copy()
            
            # Calculer le pourcentage de réussite
            shooting_stats['% Réussite'] = (
                (shooting_stats['goals'] / shooting_stats['shots'] * 100)
                .round(2)
            )
            
            # Renommer les colonnes
            shooting_stats = shooting_stats.rename(columns={
                'team_name': 'Équipe',
                'goals': 'Buts',
                'shots': 'Tirs'
            })
            
            # Trier par pourcentage de réussite
            shooting_stats = shooting_stats.sort_values('% Réussite', ascending=False).reset_index(drop=True)
            shooting_stats.insert(0, 'Rang', range(1, len(shooting_stats) + 1))
            
            # Réorganiser les colonnes pour mettre % Réussite après Équipe
            shooting_stats = shooting_stats[['Rang', 'Équipe', '% Réussite', 'Buts', 'Tirs']]
            
            st.dataframe(
                shooting_stats,
                use_container_width=True,
                hide_index=True
            )
            
            # Statistiques rapides
            col1, col2, col3 = st.columns(3)
            with col1:
                best_shooting = shooting_stats.iloc[0]
                st.metric(
                    "Meilleur % de réussite",
                    best_shooting['Équipe'],
                    f"{best_shooting['% Réussite']:.2f}%"
                )
            with col2:
                avg_shooting = shooting_stats['% Réussite'].mean()
                st.metric(
                    "Moyenne de la ligue",
                    f"{avg_shooting:.2f}%"
                )
            with col3:
                total_shots = shooting_stats['Tirs'].sum()
                st.metric(
                    "Total de tirs",
                    f"{int(total_shots)}"
                )
            
            st.download_button(
                label="📥 Télécharger les statistiques CSV",
                data=shooting_stats.to_csv(index=False).encode('utf-8'),
                file_name='stats_pourcentage_reussite.csv',
                mime='text/csv',
            )
        else:
            st.info("Aucune statistique de joueur disponible.")
    else:
        st.info("Aucune statistique de joueur disponible.")
