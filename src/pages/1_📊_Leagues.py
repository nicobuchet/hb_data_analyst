"""
Page Ligues - Voir et analyser les informations des ligues
"""
import streamlit as st
import pandas as pd
from src.database import get_leagues

st.set_page_config(page_title="Ligues", page_icon="📊", layout="wide")

# Sidebar
with st.sidebar:
    st.markdown("## 🤾 Navigation")
    st.markdown("---")
    st.info("**Page actuelle:** Ligues")

st.title("📊 Ligues")
st.write("Parcourir et analyser les informations des ligues de handball.")

try:
    # Charger les données des ligues
    leagues_df = get_leagues()
    
    if leagues_df.empty:
        st.info("Aucune ligue trouvée dans la base de données.")
    else:
        # Afficher les statistiques
        st.markdown("### Statistiques des ligues")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Ligues totales", len(leagues_df))
        
        with col2:
            if 'season' in leagues_df.columns:
                unique_seasons = leagues_df['season'].nunique()
                st.metric("Saisons", unique_seasons)
        
        with col3:
            if 'group_name' in leagues_df.columns:
                unique_groups = leagues_df['group_name'].nunique()
                st.metric("Groupes", unique_groups)
        
        # Filtres
        st.markdown("---")
        st.markdown("### Filtrer les ligues")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'season' in leagues_df.columns:
                seasons = ['Tous'] + sorted(leagues_df['season'].dropna().unique().tolist())
                selected_season = st.selectbox("Saison", seasons)
        
        with col2:
            if 'group_name' in leagues_df.columns:
                groups = ['Tous'] + sorted(leagues_df['group_name'].dropna().unique().tolist())
                selected_group = st.selectbox("Groupe", groups)
        
        # Appliquer les filtres
        filtered_df = leagues_df.copy()
        
        if 'season' in leagues_df.columns and selected_season != 'Tous':
            filtered_df = filtered_df[filtered_df['season'] == selected_season]
        
        if 'group_name' in leagues_df.columns and selected_group != 'Tous':
            filtered_df = filtered_df[filtered_df['group_name'] == selected_group]
        
        # Afficher les données filtrées
        st.markdown("---")
        st.markdown(f"### Données des ligues ({len(filtered_df)} enregistrements)")
        
        # Afficher le dataframe
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Option d'export
        st.download_button(
            label="📥 Télécharger CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name='donnees_ligues.csv',
            mime='text/csv',
        )

except Exception as e:
    st.error(f"Erreur lors du chargement des données des ligues : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
