"""
Page Rapport de Club - Rechercher et analyser les statistiques d'un club
"""
import streamlit as st
import pandas as pd
import traceback
from src.database import get_matches, get_teams, get_player_stats

st.set_page_config(page_title="Rapport de Club", page_icon="🏟️", layout="wide")

# Cacher la navigation par défaut de Streamlit
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🤾 Navigation")
    st.markdown("---")
    
    st.page_link("app.py", label="Accueil", icon="🏠")
    st.page_link("pages/2_🏆_Rankings.py", label="Classements", icon="🏆")
    st.page_link("pages/3_📈_Team_Stats.py", label="Statistiques d'équipes", icon="📈")
    st.page_link("pages/4_👤_Player_Stats.py", label="Statistiques de joueurs", icon="👤")
    st.page_link("pages/5_🏟️_Club_Report.py", label="Rapport de Club", icon="🏟️")
    
    st.markdown("---")
    st.info("**Page actuelle:** Rapport de Club")

st.title("🏟️ Rapport de Club")
st.write("Recherchez un club et consultez ses statistiques détaillées.")

try:
    # Charger les données
    matches_df = get_matches()
    teams_df = get_teams()
    player_stats_df = get_player_stats()
    
    if teams_df.empty:
        st.info("Aucune équipe disponible. Importez des matchs pour commencer !")
    else:
        # Sélection du club
        st.markdown("### 🔍 Recherche de club")
        
        team_names = sorted(teams_df['name'].unique().tolist())
        selected_team = st.selectbox(
            "Sélectionnez un club",
            options=team_names,
            key="team_selector"
        )
        
        if selected_team:
            # Récupérer l'ID de l'équipe
            team_id = teams_df[teams_df['name'] == selected_team]['id'].iloc[0]
            
            st.markdown("---")
            st.markdown(f"## 📊 Rapport de {selected_team}")
            
            # Filtrer les matchs de cette équipe
            team_matches = matches_df[
                (matches_df['home_team_id'] == team_id) | 
                (matches_df['away_team_id'] == team_id)
            ].copy()
            
            if team_matches.empty:
                st.info(f"Aucun match trouvé pour {selected_team}")
            else:
                # === STATISTIQUES GÉNÉRALES ===
                st.markdown("### 📈 Statistiques Générales")
                
                # Calculer les statistiques
                total_matches = len(team_matches)
                
                # Calculer victoires, nuls, défaites
                wins = 0
                draws = 0
                losses = 0
                goals_for = 0
                goals_against = 0
                home_matches = 0
                away_matches = 0
                
                for _, match in team_matches.iterrows():
                    is_home = match['home_team_id'] == team_id
                    
                    if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                        if is_home:
                            home_matches += 1
                            team_score = match['final_score_home']
                            opponent_score = match['final_score_away']
                        else:
                            away_matches += 1
                            team_score = match['final_score_away']
                            opponent_score = match['final_score_home']
                        
                        goals_for += team_score
                        goals_against += opponent_score
                        
                        if team_score > opponent_score:
                            wins += 1
                        elif team_score == opponent_score:
                            draws += 1
                        else:
                            losses += 1
                
                # Points (3 pts victoire, 2 pts nul, 1 pt défaite)
                points = wins * 3 + draws * 2 + losses * 1
                
                # Afficher les métriques principales
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Matchs joués", total_matches)
                
                with col2:
                    st.metric("Victoires", wins)
                
                with col3:
                    st.metric("Nuls", draws)
                
                with col4:
                    st.metric("Défaites", losses)
                
                with col5:
                    st.metric("Points", points)
                
                st.markdown("---")
                
                # Statistiques de buts
                col6, col7, col8, col9 = st.columns(4)
                
                with col6:
                    st.metric("Buts marqués", int(goals_for))
                
                with col7:
                    st.metric("Buts encaissés", int(goals_against))
                
                with col8:
                    goal_diff = int(goals_for - goals_against)
                    st.metric("Différence de buts", goal_diff, delta=goal_diff)
                
                with col9:
                    avg_goals_for = goals_for / total_matches if total_matches > 0 else 0
                    st.metric("Moy. buts/match", f"{avg_goals_for:.2f}")
                
                st.markdown("---")
                
                # Statistiques domicile/extérieur
                st.markdown("### 🏠 Performance Domicile vs Extérieur")
                
                # Calculer les stats domicile
                home_wins = 0
                home_draws = 0
                home_losses = 0
                home_goals_for = 0
                home_goals_against = 0
                
                for _, match in team_matches[team_matches['home_team_id'] == team_id].iterrows():
                    if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                        home_goals_for += match['final_score_home']
                        home_goals_against += match['final_score_away']
                        
                        if match['final_score_home'] > match['final_score_away']:
                            home_wins += 1
                        elif match['final_score_home'] == match['final_score_away']:
                            home_draws += 1
                        else:
                            home_losses += 1
                
                # Calculer les stats extérieur
                away_wins = 0
                away_draws = 0
                away_losses = 0
                away_goals_for = 0
                away_goals_against = 0
                
                for _, match in team_matches[team_matches['away_team_id'] == team_id].iterrows():
                    if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                        away_goals_for += match['final_score_away']
                        away_goals_against += match['final_score_home']
                        
                        if match['final_score_away'] > match['final_score_home']:
                            away_wins += 1
                        elif match['final_score_away'] == match['final_score_home']:
                            away_draws += 1
                        else:
                            away_losses += 1
                
                # Afficher en grille
                st.markdown("#### 🏠 À domicile")
                col_h1, col_h2, col_h3, col_h4, col_h5, col_h6 = st.columns(6)
                
                with col_h1:
                    st.metric("Matchs", home_matches)
                with col_h2:
                    st.metric("Victoires", home_wins)
                with col_h3:
                    st.metric("Nuls", home_draws)
                with col_h4:
                    st.metric("Défaites", home_losses)
                with col_h5:
                    st.metric("Buts pour", int(home_goals_for))
                with col_h6:
                    st.metric("Buts contre", int(home_goals_against))
                
                st.markdown("#### ✈️ À l'extérieur")
                col_a1, col_a2, col_a3, col_a4, col_a5, col_a6 = st.columns(6)
                
                with col_a1:
                    st.metric("Matchs", away_matches)
                with col_a2:
                    st.metric("Victoires", away_wins)
                with col_a3:
                    st.metric("Nuls", away_draws)
                with col_a4:
                    st.metric("Défaites", away_losses)
                with col_a5:
                    st.metric("Buts pour", int(away_goals_for))
                with col_a6:
                    st.metric("Buts contre", int(away_goals_against))
                
                st.markdown("---")
                
                # === MEILLEURE VICTOIRE ET PIRE DÉFAITE ===
                st.markdown("### 🏆 Meilleure Victoire & 😞 Pire Défaite")
                
                # Calculer le classement de toutes les équipes
                def calculate_team_ranking(matches_df, teams_df):
                    team_stats = {}
                    
                    for tid in teams_df['id'].unique():
                        wins = 0
                        draws = 0
                        losses = 0
                        goals_for = 0
                        goals_against = 0
                        
                        # Matchs à domicile
                        home_matches = matches_df[matches_df['home_team_id'] == tid]
                        for _, match in home_matches.iterrows():
                            if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                                goals_for += match['final_score_home']
                                goals_against += match['final_score_away']
                                if match['final_score_home'] > match['final_score_away']:
                                    wins += 1
                                elif match['final_score_home'] == match['final_score_away']:
                                    draws += 1
                                else:
                                    losses += 1
                        
                        # Matchs à l'extérieur
                        away_matches = matches_df[matches_df['away_team_id'] == tid]
                        for _, match in away_matches.iterrows():
                            if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                                goals_for += match['final_score_away']
                                goals_against += match['final_score_home']
                                if match['final_score_away'] > match['final_score_home']:
                                    wins += 1
                                elif match['final_score_away'] == match['final_score_home']:
                                    draws += 1
                                else:
                                    losses += 1
                        
                        points = wins * 3 + draws * 2 + losses * 1
                        goal_diff = goals_for - goals_against
                        team_stats[tid] = {
                            'points': points,
                            'goal_diff': goal_diff,
                            'goals_for': goals_for
                        }
                    
                    # Trier les équipes par points, puis différence de buts, puis buts marqués
                    sorted_teams = sorted(team_stats.items(), 
                                        key=lambda x: (x[1]['points'], x[1]['goal_diff'], x[1]['goals_for']), 
                                        reverse=True)
                    
                    # Créer un dictionnaire avec les rangs
                    team_ranks = {}
                    for rank, (tid, stats) in enumerate(sorted_teams, 1):
                        team_ranks[tid] = rank
                    
                    return team_ranks
                
                team_rankings = calculate_team_ranking(matches_df, teams_df)
                
                # Fonction pour formater le rang avec suffixe ordinal
                def format_rank(rank):
                    if rank == 1:
                        return "1er"
                    else:
                        return f"{rank}e"
                
                # Trouver la meilleure victoire et la pire défaite
                best_win = None
                worst_defeat = None
                best_win_opponent_rank = float('inf')  # Plus petit rang = meilleure équipe
                worst_defeat_opponent_rank = -1  # Plus grand rang = moins bonne équipe
                
                for _, match in team_matches.iterrows():
                    if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                        is_home = match['home_team_id'] == team_id
                        
                        if is_home:
                            team_score = match['final_score_home']
                            opponent_score = match['final_score_away']
                            opponent_id = match['away_team_id']
                        else:
                            team_score = match['final_score_away']
                            opponent_score = match['final_score_home']
                            opponent_id = match['home_team_id']
                        
                        opponent_rank = team_rankings.get(opponent_id, 999)
                        opponent_name = teams_df[teams_df['id'] == opponent_id]['name'].iloc[0]
                        
                        # Victoire - chercher contre l'équipe la mieux classée (rang le plus bas)
                        if team_score > opponent_score:
                            if opponent_rank < best_win_opponent_rank:
                                best_win_opponent_rank = opponent_rank
                                best_win = {
                                    'opponent': opponent_name,
                                    'score_for': int(team_score),
                                    'score_against': int(opponent_score),
                                    'date': match['match_date'],
                                    'is_home': is_home,
                                    'opponent_rank': opponent_rank
                                }
                        
                        # Défaite - chercher contre l'équipe la moins bien classée (rang le plus élevé)
                        elif team_score < opponent_score:
                            if opponent_rank > worst_defeat_opponent_rank:
                                worst_defeat_opponent_rank = opponent_rank
                                worst_defeat = {
                                    'opponent': opponent_name,
                                    'score_for': int(team_score),
                                    'score_against': int(opponent_score),
                                    'date': match['match_date'],
                                    'is_home': is_home,
                                    'opponent_rank': opponent_rank
                                }
                
                col_win, col_defeat = st.columns(2)
                
                with col_win:
                    st.markdown("#### 🏆 Meilleure Victoire")
                    if best_win:
                        location = "🏠 Domicile" if best_win['is_home'] else "✈️ Extérieur"
                        rank_text = format_rank(best_win['opponent_rank'])
                        st.success(f"**{best_win['opponent']}** ({rank_text})")
                        st.metric(
                            "Score",
                            f"{best_win['score_for']} - {best_win['score_against']}",
                            delta=f"+{best_win['score_for'] - best_win['score_against']}"
                        )
                        st.caption(f"{location} • {pd.to_datetime(best_win['date']).strftime('%d/%m/%Y')}")
                    else:
                        st.info("Aucune victoire enregistrée")
                
                with col_defeat:
                    st.markdown("#### 😞 Pire Défaite")
                    if worst_defeat:
                        location = "🏠 Domicile" if worst_defeat['is_home'] else "✈️ Extérieur"
                        rank_text = format_rank(worst_defeat['opponent_rank'])
                        st.error(f"**{worst_defeat['opponent']}** ({rank_text})")
                        st.metric(
                            "Score",
                            f"{worst_defeat['score_for']} - {worst_defeat['score_against']}",
                            delta=f"{worst_defeat['score_for'] - worst_defeat['score_against']}"
                        )
                        st.caption(f"{location} • {pd.to_datetime(worst_defeat['date']).strftime('%d/%m/%Y')}")
                    else:
                        st.info("Aucune défaite enregistrée")
                
                st.markdown("---")
                
                # === PLUS LARGE VICTOIRE ET PLUS LARGE DÉFAITE ===
                st.markdown("### 🎯 Plus Large Victoire & 💔 Plus Large Défaite")
                
                # Trouver la plus large victoire et la plus large défaite
                largest_win = None
                largest_defeat = None
                largest_win_diff = 0
                largest_defeat_diff = 0
                
                for _, match in team_matches.iterrows():
                    if pd.notna(match['final_score_home']) and pd.notna(match['final_score_away']):
                        is_home = match['home_team_id'] == team_id
                        
                        if is_home:
                            team_score = match['final_score_home']
                            opponent_score = match['final_score_away']
                            opponent_id = match['away_team_id']
                        else:
                            team_score = match['final_score_away']
                            opponent_score = match['final_score_home']
                            opponent_id = match['home_team_id']
                        
                        goal_diff = abs(team_score - opponent_score)
                        opponent_name = teams_df[teams_df['id'] == opponent_id]['name'].iloc[0]
                        
                        # Victoire - chercher la plus grande différence
                        if team_score > opponent_score:
                            if goal_diff > largest_win_diff:
                                largest_win_diff = goal_diff
                                largest_win = {
                                    'opponent': opponent_name,
                                    'score_for': int(team_score),
                                    'score_against': int(opponent_score),
                                    'date': match['match_date'],
                                    'is_home': is_home,
                                    'goal_diff': int(goal_diff)
                                }
                        
                        # Défaite - chercher la plus grande différence
                        elif team_score < opponent_score:
                            if goal_diff > largest_defeat_diff:
                                largest_defeat_diff = goal_diff
                                largest_defeat = {
                                    'opponent': opponent_name,
                                    'score_for': int(team_score),
                                    'score_against': int(opponent_score),
                                    'date': match['match_date'],
                                    'is_home': is_home,
                                    'goal_diff': int(goal_diff)
                                }
                
                col_large_win, col_large_defeat = st.columns(2)
                
                with col_large_win:
                    st.markdown("#### 🎯 Plus Large Victoire")
                    if largest_win:
                        location = "🏠 Domicile" if largest_win['is_home'] else "✈️ Extérieur"
                        st.success(f"**{largest_win['opponent']}**")
                        st.metric(
                            "Score",
                            f"{largest_win['score_for']} - {largest_win['score_against']}",
                            delta=f"+{largest_win['goal_diff']} buts"
                        )
                        st.caption(f"{location} • {pd.to_datetime(largest_win['date']).strftime('%d/%m/%Y')}")
                    else:
                        st.info("Aucune victoire enregistrée")
                
                with col_large_defeat:
                    st.markdown("#### 💔 Plus Large Défaite")
                    if largest_defeat:
                        location = "🏠 Domicile" if largest_defeat['is_home'] else "✈️ Extérieur"
                        st.error(f"**{largest_defeat['opponent']}**")
                        st.metric(
                            "Score",
                            f"{largest_defeat['score_for']} - {largest_defeat['score_against']}",
                            delta=f"-{largest_defeat['goal_diff']} buts"
                        )
                        st.caption(f"{location} • {pd.to_datetime(largest_defeat['date']).strftime('%d/%m/%Y')}")
                    else:
                        st.info("Aucune défaite enregistrée")
                
                st.markdown("---")
                
                # === STATISTIQUES DES JOUEURS ===
                if not player_stats_df.empty:
                    st.markdown("### 👥 Statistiques des Joueurs")
                    
                    # Filtrer les stats des joueurs de cette équipe
                    team_player_stats = player_stats_df[
                        (player_stats_df['team_name'] == selected_team) & 
                        (player_stats_df['is_official'] == False)
                    ].copy()
                    
                    if not team_player_stats.empty:
                        # Agréger par joueur
                        player_summary = team_player_stats.groupby('player_name').agg({
                            'match_id': 'nunique',
                            'goals': 'sum',
                            'shots': 'sum',
                            'goals_7m': 'sum',
                            'saves': 'sum',
                            'yellow_cards': 'sum',
                            'two_minutes': 'sum',
                            'red_cards': 'sum',
                            'blue_cards': 'sum'
                        }).reset_index()
                        
                        # Total sanctions
                        player_summary['total_sanctions'] = (
                            player_summary['yellow_cards'] + 
                            player_summary['two_minutes'] + 
                            player_summary['red_cards'] + 
                            player_summary['blue_cards']
                        )
                        
                        # Calculer l'efficacité
                        player_summary['efficiency'] = player_summary.apply(
                            lambda row: round(row['goals'] / row['shots'] * 100, 1) if row['shots'] > 0 else 0,
                            axis=1
                        )
                        
                        # Créer les widgets Top 5
                        col_widget1, col_widget2 = st.columns(2)
                        
                        # Widget 1: Top 5 Buteurs
                        with col_widget1:
                            st.markdown("#### ⚽ Top 5 Buteurs")
                            top_scorers = player_summary[player_summary['goals'] > 0].nlargest(5, 'goals').copy()
                            
                            if not top_scorers.empty:
                                top_scorers_display = top_scorers[['player_name', 'goals', 'efficiency']].copy()
                                top_scorers_display = top_scorers_display.rename(columns={
                                    'player_name': 'Joueur',
                                    'goals': 'Buts',
                                    'efficiency': 'Eff. %'
                                })
                                top_scorers_display.insert(0, 'Rang', range(1, len(top_scorers_display) + 1))
                                
                                st.dataframe(
                                    top_scorers_display,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Rang": st.column_config.NumberColumn("Rang", width="small"),
                                        "Joueur": st.column_config.TextColumn("Joueur", width="medium"),
                                        "Buts": st.column_config.NumberColumn("Buts", width="small"),
                                        "Eff. %": st.column_config.NumberColumn("Eff. %", width="small", format="%.1f")
                                    }
                                )
                            else:
                                st.info("Aucun buteur")
                        
                        # Widget 2: Top 5 Gardiens
                        with col_widget2:
                            st.markdown("#### 🧤 Top 5 Gardiens")
                            top_goalkeepers = player_summary[player_summary['saves'] > 0].nlargest(5, 'saves').copy()
                            
                            if not top_goalkeepers.empty:
                                top_goalkeepers_display = top_goalkeepers[['player_name', 'saves']].copy()
                                top_goalkeepers_display = top_goalkeepers_display.rename(columns={
                                    'player_name': 'Joueur',
                                    'saves': 'Arrêts'
                                })
                                top_goalkeepers_display.insert(0, 'Rang', range(1, len(top_goalkeepers_display) + 1))
                                
                                st.dataframe(
                                    top_goalkeepers_display,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Rang": st.column_config.NumberColumn("Rang", width="small"),
                                        "Joueur": st.column_config.TextColumn("Joueur", width="medium"),
                                        "Arrêts": st.column_config.NumberColumn("Arrêts", width="small")
                                    }
                                )
                            else:
                                st.info("Aucun gardien")
                        
                        st.markdown("---")
                        
                        col_widget3, col_widget4 = st.columns(2)
                        
                        # Widget 3: Top 5 Spécialistes 7m
                        with col_widget3:
                            st.markdown("#### 🎯 Top 5 Spécialistes 7m")
                            top_7m = player_summary[player_summary['goals_7m'] > 0].nlargest(5, 'goals_7m').copy()
                            
                            if not top_7m.empty:
                                top_7m_display = top_7m[['player_name', 'goals_7m']].copy()
                                top_7m_display = top_7m_display.rename(columns={
                                    'player_name': 'Joueur',
                                    'goals_7m': 'Buts 7m'
                                })
                                top_7m_display.insert(0, 'Rang', range(1, len(top_7m_display) + 1))
                                
                                st.dataframe(
                                    top_7m_display,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Rang": st.column_config.NumberColumn("Rang", width="small"),
                                        "Joueur": st.column_config.TextColumn("Joueur", width="medium"),
                                        "Buts 7m": st.column_config.NumberColumn("Buts 7m", width="small")
                                    }
                                )
                            else:
                                st.info("Aucun spécialiste 7m")
                        
                        # Widget 4: Top 5 Joueurs avec le plus de sanctions
                        with col_widget4:
                            st.markdown("#### ⚠️ Top 5 Sanctions")
                            top_sanctions = player_summary[player_summary['total_sanctions'] > 0].nlargest(5, 'total_sanctions').copy()
                            
                            if not top_sanctions.empty:
                                top_sanctions_display = top_sanctions[['player_name', 'total_sanctions', 'yellow_cards', 'two_minutes', 'red_cards', 'blue_cards']].copy()
                                top_sanctions_display = top_sanctions_display.rename(columns={
                                    'player_name': 'Joueur',
                                    'total_sanctions': 'Total',
                                    'yellow_cards': '🟨',
                                    'two_minutes': '⏱️',
                                    'red_cards': '🟥',
                                    'blue_cards': '🟦'
                                })
                                top_sanctions_display.insert(0, 'Rang', range(1, len(top_sanctions_display) + 1))
                                
                                st.dataframe(
                                    top_sanctions_display,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Rang": st.column_config.NumberColumn("Rang", width="small"),
                                        "Joueur": st.column_config.TextColumn("Joueur", width="medium"),
                                        "Total": st.column_config.NumberColumn("Total", width="small"),
                                        "🟨": st.column_config.NumberColumn("🟨", width="small"),
                                        "⏱️": st.column_config.NumberColumn("⏱️", width="small"),
                                        "🟥": st.column_config.NumberColumn("🟥", width="small"),
                                        "🟦": st.column_config.NumberColumn("🟦", width="small")
                                    }
                                )
                            else:
                                st.info("Aucune sanction")
                    else:
                        st.info(f"Aucune statistique de joueur disponible pour {selected_team}")
                else:
                    st.info("Aucune statistique de joueur disponible dans la base de données")

except Exception as e:
    st.error(f"Erreur lors du chargement des données : {str(e)}")
    st.info("Veuillez vous assurer que votre connexion Supabase est correctement configurée.")
    with st.expander("Détails de l'erreur"):
        st.code(traceback.format_exc())
