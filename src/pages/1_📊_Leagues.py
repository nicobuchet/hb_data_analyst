"""
Leagues Page - View and analyze league information
"""
import streamlit as st
import pandas as pd
from src.database import get_leagues

st.set_page_config(page_title="Leagues", page_icon="📊", layout="wide")

st.title("📊 Leagues")
st.write("Browse and analyze handball league information.")

try:
    # Load leagues data
    leagues_df = get_leagues()
    
    if leagues_df.empty:
        st.info("No leagues found in the database.")
    else:
        # Display statistics
        st.markdown("### League Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Leagues", len(leagues_df))
        
        with col2:
            if 'season' in leagues_df.columns:
                unique_seasons = leagues_df['season'].nunique()
                st.metric("Seasons", unique_seasons)
        
        with col3:
            if 'group_name' in leagues_df.columns:
                unique_groups = leagues_df['group_name'].nunique()
                st.metric("Groups", unique_groups)
        
        # Filters
        st.markdown("---")
        st.markdown("### Filter Leagues")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'season' in leagues_df.columns:
                seasons = ['All'] + sorted(leagues_df['season'].dropna().unique().tolist())
                selected_season = st.selectbox("Season", seasons)
        
        with col2:
            if 'group_name' in leagues_df.columns:
                groups = ['All'] + sorted(leagues_df['group_name'].dropna().unique().tolist())
                selected_group = st.selectbox("Group", groups)
        
        # Apply filters
        filtered_df = leagues_df.copy()
        
        if 'season' in leagues_df.columns and selected_season != 'All':
            filtered_df = filtered_df[filtered_df['season'] == selected_season]
        
        if 'group_name' in leagues_df.columns and selected_group != 'All':
            filtered_df = filtered_df[filtered_df['group_name'] == selected_group]
        
        # Display filtered data
        st.markdown("---")
        st.markdown(f"### Leagues Data ({len(filtered_df)} records)")
        
        # Display dataframe
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Export option
        st.download_button(
            label="📥 Download CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name='leagues_data.csv',
            mime='text/csv',
        )

except Exception as e:
    st.error(f"Error loading leagues data: {str(e)}")
    st.info("Please ensure your Supabase connection is properly configured.")
