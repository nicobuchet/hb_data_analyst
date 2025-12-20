"""
Database connection and utility functions for Supabase
"""
from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_KEY
import pandas as pd


def get_supabase_client() -> Client:
    """Create and return a Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def query_to_dataframe(table_name: str, query_params: dict = None) -> pd.DataFrame:
    """
    Query a Supabase table and return results as a pandas DataFrame
    Automatically handles pagination to fetch all rows.
    
    Args:
        table_name: Name of the table to query
        query_params: Optional dictionary with query parameters like filters, limit, etc.
    
    Returns:
        pandas DataFrame with query results
    """
    client = get_supabase_client()
    
    # If a specific limit is requested, use single query
    if query_params and "limit" in query_params:
        query = client.table(table_name).select("*")
        query = query.limit(query_params["limit"])
        if "order" in query_params:
            query = query.order(query_params["order"])
        response = query.execute()
        return pd.DataFrame(response.data)
    
    # Otherwise, fetch all rows with pagination
    all_data = []
    page_size = 1000
    offset = 0
    
    while True:
        query = client.table(table_name).select("*").range(offset, offset + page_size - 1)
        
        if query_params and "order" in query_params:
            query = query.order(query_params["order"])
        
        response = query.execute()
        data = response.data
        
        if not data:
            break
        
        all_data.extend(data)
        
        # If we got fewer rows than page_size, we've reached the end
        if len(data) < page_size:
            break
        
        offset += page_size
    
    return pd.DataFrame(all_data)


def get_leagues() -> pd.DataFrame:
    """Get all leagues"""
    return query_to_dataframe("leagues")


def get_teams() -> pd.DataFrame:
    """Get all teams"""
    return query_to_dataframe("teams")


def get_players() -> pd.DataFrame:
    """Get all players"""
    return query_to_dataframe("players")


def get_matches() -> pd.DataFrame:
    """Get all matches"""
    return query_to_dataframe("matches")


def get_player_stats() -> pd.DataFrame:
    """Get all player statistics"""
    return query_to_dataframe("player_stats")


def get_actions() -> pd.DataFrame:
    """Get all match actions"""
    return query_to_dataframe("actions")


def get_match_details(match_id: int) -> dict:
    """
    Get detailed information about a specific match including stats and actions
    
    Args:
        match_id: ID of the match
    
    Returns:
        Dictionary with match info, player stats, and actions
    """
    client = get_supabase_client()
    
    # Get match info
    match = client.table("matches").select("*").eq("id", match_id).execute()
    
    # Get player stats for this match
    stats = client.table("player_stats").select("*").eq("match_id", match_id).execute()
    
    # Get actions for this match
    actions = client.table("actions").select("*").eq("match_id", match_id).order("period, time").execute()
    
    return {
        "match": pd.DataFrame(match.data) if match.data else pd.DataFrame(),
        "stats": pd.DataFrame(stats.data) if stats.data else pd.DataFrame(),
        "actions": pd.DataFrame(actions.data) if actions.data else pd.DataFrame()
    }
