"""
Tab: Buts encaissés
"""
import streamlit as st
import pandas as pd


def render(matches_df: pd.DataFrame, teams_df: pd.DataFrame, player_stats_df: pd.DataFrame, stats_df: pd.DataFrame):
    """Render the goals conceded tab"""
    st.markdown("### 🛡️ Classement des buts encaissés")
    
    if stats_df is not None:
        # Trier par buts encaissés (ordre croissant = meilleure défense)
        goals_against_df = stats_df[['Équipe', 'J', 'Buts encaissés', 'Moy encaissés', 'Encaissés dom.', 'Encaissés ext.']].copy()
        goals_against_df = goals_against_df.sort_values('Buts encaissés', ascending=True).reset_index(drop=True)
        goals_against_df.insert(0, 'Rang', range(1, len(goals_against_df) + 1))
        
        st.dataframe(
            goals_against_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Statistiques rapides
        col1, col2, col3 = st.columns(3)
        with col1:
            best_defense = goals_against_df.iloc[0]
            st.metric(
                "Meilleure défense",
                best_defense['Équipe'],
                f"{int(best_defense['Buts encaissés'])} buts encaissés"
            )
        with col2:
            avg_goals_against = stats_df['Buts encaissés'].mean()
            st.metric(
                "Moyenne de la ligue",
                f"{avg_goals_against:.1f} buts"
            )
        with col3:
            total_goals_against = stats_df['Buts encaissés'].sum()
            st.metric(
                "Total de buts encaissés",
                f"{int(total_goals_against)} buts"
            )
        
        st.download_button(
            label="📥 Télécharger les statistiques CSV",
            data=goals_against_df.to_csv(index=False).encode('utf-8'),
            file_name='stats_buts_encaisses.csv',
            mime='text/csv',
        )
    else:
        st.info("Aucun match terminé trouvé.")
