"""
Utility functions for team statistics
"""
import pandas as pd


def calculate_team_matches(matches_df: pd.DataFrame, teams_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the number of matches played by each team"""
    team_matches = []
    for team_id in teams_df['id'].unique():
        team_name = teams_df[teams_df['id'] == team_id]['name'].iloc[0]
        # Compter les matchs à domicile et à l'extérieur
        home_matches = matches_df[
            (matches_df['home_team_id'] == team_id) & 
            (matches_df['final_score_home'].notna())
        ]
        away_matches = matches_df[
            (matches_df['away_team_id'] == team_id) & 
            (matches_df['final_score_away'].notna())
        ]
        total_matches = len(home_matches) + len(away_matches)
        if total_matches > 0:
            team_matches.append({'team_name': team_name, 'matches': total_matches})
    
    return pd.DataFrame(team_matches)


def calculate_goal_stats(matches_df: pd.DataFrame, teams_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate goal statistics for all teams"""
    goal_stats = []
    
    for team_id in teams_df['id'].unique():
        team_name = teams_df[teams_df['id'] == team_id]['name'].iloc[0]
        
        # Matchs à domicile
        home_matches = matches_df[matches_df['home_team_id'] == team_id]
        # Matchs à l'extérieur
        away_matches = matches_df[matches_df['away_team_id'] == team_id]
        
        # Initialiser les compteurs
        total_goals_for = 0
        total_goals_against = 0
        home_goals_for = 0
        away_goals_for = 0
        home_goals_against = 0
        away_goals_against = 0
        matches_played = 0
        
        # Calculer les buts à domicile
        for _, match in home_matches.iterrows():
            if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                home_goals_for += match['final_score_home']
                home_goals_against += match['final_score_away']
                total_goals_for += match['final_score_home']
                total_goals_against += match['final_score_away']
                matches_played += 1
        
        # Calculer les buts à l'extérieur
        for _, match in away_matches.iterrows():
            if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                away_goals_for += match['final_score_away']
                away_goals_against += match['final_score_home']
                total_goals_for += match['final_score_away']
                total_goals_against += match['final_score_home']
                matches_played += 1
        
        if matches_played > 0:
            goal_stats.append({
                'Équipe': team_name,
                'J': matches_played,
                'Buts marqués': int(total_goals_for),
                'Buts encaissés': int(total_goals_against),
                'Diff': int(total_goals_for - total_goals_against),
                'Moy marqués': round(total_goals_for / matches_played, 2),
                'Moy encaissés': round(total_goals_against / matches_played, 2),
                'Buts dom.': int(home_goals_for),
                'Buts ext.': int(away_goals_for),
                'Encaissés dom.': int(home_goals_against),
                'Encaissés ext.': int(away_goals_against),
            })
    
    if goal_stats:
        return pd.DataFrame(goal_stats)
    else:
        return None
