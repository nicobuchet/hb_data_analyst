"""
Handball Analytics Dashboard - Main Application
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Handball Analytics Dashboard",
    page_icon="🤾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 3rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .feature-box {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Main content
st.markdown('<div class="main-header">🤾 Handball Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Comprehensive handball match data analysis and visualization</div>', unsafe_allow_html=True)

# Welcome message
st.write("---")
st.markdown("### Welcome to the Handball Analytics Dashboard!")
st.write("""
This dashboard provides comprehensive analytics and insights from handball match data stored in Supabase.
Explore different sections using the sidebar navigation to access detailed information about leagues, teams, players, and matches.
""")

# Quick stats section
st.write("---")
st.markdown("### 📊 Quick Overview")

try:
    from src.database import get_leagues, get_teams, get_players, get_matches
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        leagues_df = get_leagues()
        st.metric("Total Leagues", len(leagues_df))
    
    with col2:
        teams_df = get_teams()
        st.metric("Total Teams", len(teams_df))
    
    with col3:
        players_df = get_players()
        st.metric("Total Players", len(players_df))
    
    with col4:
        matches_df = get_matches()
        st.metric("Total Matches", len(matches_df))

except Exception as e:
    st.warning("⚠️ Could not load database statistics. Please ensure your Supabase connection is properly configured.")
    st.info("💡 Create a `.env` file in the root directory with your Supabase credentials. See `.env.example` for the required format.")
    with st.expander("Error details"):
        st.error(str(e))

# Features section
st.write("---")
st.markdown("### 🎯 Dashboard Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h4>📈 Data Exploration</h4>
        <ul>
            <li>Browse leagues, teams, and players</li>
            <li>View match results and statistics</li>
            <li>Analyze player performance metrics</li>
            <li>Track match actions and events</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h4>🔍 Advanced Analytics</h4>
        <ul>
            <li>Player comparison tools</li>
            <li>Team performance trends</li>
            <li>Statistical insights</li>
            <li>Custom data filtering</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h4>📊 Visualizations</h4>
        <ul>
            <li>Interactive charts and graphs</li>
            <li>Match timeline analysis</li>
            <li>Performance heatmaps</li>
            <li>Statistical distributions</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h4>⚙️ Database Structure</h4>
        <ul>
            <li>Leagues: Competition information</li>
            <li>Teams: Team profiles</li>
            <li>Players: Player profiles and team associations</li>
            <li>Matches: Game results and scores</li>
            <li>Player Stats: Detailed performance metrics</li>
            <li>Actions: Chronological match events</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Getting started section
st.write("---")
st.markdown("### 🚀 Getting Started")
st.info("""
1. **Configure Database**: Set up your `.env` file with Supabase credentials
2. **Navigate**: Use the sidebar to explore different sections
3. **Filter**: Apply filters to narrow down your data view
4. **Analyze**: Interact with visualizations and tables
5. **Export**: Download data for further analysis (feature coming soon)
""")

# Footer
st.write("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>Built with Streamlit 🎈 | Data powered by Supabase 🚀</p>
</div>
""", unsafe_allow_html=True)
