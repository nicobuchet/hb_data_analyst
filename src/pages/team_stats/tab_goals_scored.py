"""
Tab: Buts marqués
"""
import streamlit as st
import pandas as pd


def render(matches_df: pd.DataFrame, teams_df: pd.DataFrame, player_stats_df: pd.DataFrame, stats_df: pd.DataFrame):
    """Render the goals scored tab"""
    st.markdown("### 🏆 Classement des buts marqués")
    
    if stats_df is not None:
        # Trier par buts marqués
        goals_for_df = stats_df[['Équipe', 'J', 'Buts marqués', 'Moy marqués', 'Buts dom.', 'Buts ext.']].copy()
        goals_for_df = goals_for_df.sort_values('Buts marqués', ascending=False).reset_index(drop=True)
        goals_for_df.insert(0, 'Rang', range(1, len(goals_for_df) + 1))
        
        st.dataframe(
            goals_for_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Statistiques rapides
        col1, col2, col3 = st.columns(3)
        with col1:
            best_attack = goals_for_df.iloc[0]
            st.metric(
                "Meilleure attaque",
                best_attack['Équipe'],
                f"{int(best_attack['Buts marqués'])} buts"
            )
        with col2:
            avg_goals = stats_df['Buts marqués'].mean()
            st.metric(
                "Moyenne de la ligue",
                f"{avg_goals:.1f} buts"
            )
        with col3:
            total_goals = stats_df['Buts marqués'].sum()
            st.metric(
                "Total de buts",
                f"{int(total_goals)} buts"
            )
        
        st.download_button(
            label="📥 Télécharger les statistiques CSV",
            data=goals_for_df.to_csv(index=False).encode('utf-8'),
            file_name='stats_buts_marques.csv',
            mime='text/csv',
        )
    else:
        st.info("Aucun match terminé trouvé.")
