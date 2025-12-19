"""
Configuration file for Supabase connection
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to get from Streamlit secrets first (for deployment), then fall back to .env (for local dev)
try:
    import streamlit as st
    SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
except (ImportError, FileNotFoundError, KeyError):
    # Streamlit not available or secrets not configured, use environment variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in either:\n"
        "- Streamlit Cloud: App Settings > Secrets\n"
        "- Local development: .env file in project root"
    )
