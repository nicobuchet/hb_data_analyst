import camelot
import pandas as pd
from supabase import create_client, Client
import sys
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def download_pdf(url, output_path="temp_match.pdf"):
    """Download PDF from URL"""
    print(f"Downloading PDF from: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ PDF downloaded successfully to {output_path}")
        return output_path
    except Exception as e:
        print(f"✗ Error downloading PDF: {e}")
        return None

def extract_match_stats(pdf_path):
    # Lire toutes les pages
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    print("Tables trouvées:", len(tables))
    if len(tables) == 0:
        raise ValueError("Aucun tableau trouvé — vérifier le PDF ou le paramètre flavor")
        
    # Concaténer toutes les tables
    df_raw = pd.concat([t.df for t in tables], ignore_index=True)
    
    # Trouver les lignes qui contiennent les en-têtes des sections de joueurs
    club_recevant_idx = None
    club_visiteur_idx = None
    
    # Chercher les marqueurs de sections
    for idx, row in df_raw.iterrows():
        row_str = ' '.join(row.astype(str).values)
        if 'ClubRecevant' in row_str or 'ClubRecevant' in str(row.iloc[0]):
            club_recevant_idx = idx
        elif 'ClubVisiteur' in row_str or 'ClubVisiteur' in str(row.iloc[0]):
            club_visiteur_idx = idx
    
    print(f"Club Recevant trouvé à l'index: {club_recevant_idx}")
    print(f"Club Visiteur trouvé à l'index: {club_visiteur_idx}")
    
    # Extraire les deux sections de joueurs
    all_players = []
    
    # Fonction pour extraire les joueurs d'une section
    def extract_players_section(start_idx, end_idx, team_name):
        if start_idx is None:
            return []
        
        # Extraire la section
        section = df_raw.iloc[start_idx:end_idx].copy()
        
        # Trouver la ligne d'en-tête (celle qui contient "NOM prénom")
        header_idx = None
        for idx, row in section.iterrows():
            if 'NOM prénom' in str(row.values):
                header_idx = idx
                break
        
        if header_idx is None:
            return []
        
        # Extraire uniquement les lignes de joueurs (après l'en-tête)
        players_section = df_raw.iloc[header_idx:end_idx].copy()
        
        # La première ligne est l'en-tête
        header_row = players_section.iloc[0]
        
        # Trouver les indices des colonnes importantes
        col_indices = {}
        for i, val in enumerate(header_row):
            val_str = str(val).strip()
            if 'NOM prénom' in val_str:
                col_indices['name'] = i
            elif val_str == 'N°':
                col_indices['number'] = i
            elif val_str == 'Capt':
                col_indices['captain'] = i
            elif val_str == 'Buts':
                col_indices['goals'] = i
            elif val_str == 'Tirs':
                col_indices['shots'] = i
            elif val_str == '7m':
                col_indices['7m'] = i
            elif val_str == 'Arrets':
                col_indices['saves'] = i
            elif val_str == 'Av.':
                col_indices['yellow_card'] = i
            elif val_str == "2'":
                col_indices['2min'] = i
            elif val_str == 'Dis':
                col_indices['disqualification'] = i
        
        # Extraire les données des joueurs
        players = []
        for idx in range(header_idx + 1, end_idx):
            if idx >= len(df_raw):
                break
            
            row = df_raw.iloc[idx]
            
            # Vérifier si c'est une ligne de joueur (a un nom et un numéro)
            name_val = str(row.iloc[col_indices.get('name', 4)]).strip() if 'name' in col_indices else ""
            
            # Ignorer les lignes vides
            if not name_val or name_val == 'nan' or name_val == '':
                continue
            
            # Déterminer si c'est un officiel
            # Un officiel n'a pas de numéro de maillot (colonne N° vide) ou commence par "Officiel"
            is_official = False
            if 'Officiel' in name_val:
                is_official = True
            elif 'number' in col_indices:
                player_number = str(row.iloc[col_indices['number']]).strip()
                # Si pas de numéro, c'est probablement un officiel
                if not player_number or player_number == 'nan' or player_number == '':
                    is_official = True
            
            # Vérifier si le joueur est capitaine (colonne Capt contient 'X')
            is_captain = False
            if 'captain' in col_indices:
                capt_val = str(row.iloc[col_indices['captain']]).strip().upper()
                is_captain = capt_val == 'X'
            
            # Vérifier si le joueur a reçu un carton jaune (colonne Av. contient 'X')
            yellow_cards = 0
            if 'yellow_card' in col_indices:
                yellow_val = str(row.iloc[col_indices['yellow_card']]).strip().upper()
                yellow_cards = 1 if yellow_val == 'X' else 0
            
            # Récupérer les suspensions de 2 minutes
            two_min_val = row.iloc[col_indices.get('2min', 15)] if '2min' in col_indices else ''
            
            # Si 3 suspensions de 2 minutes ou plus, le joueur a un carton rouge
            red_cards = 0
            blue_cards = 0
            try:
                two_min_count = int(two_min_val) if two_min_val and str(two_min_val).strip() != '' else 0
                if two_min_count >= 3:
                    red_cards = 1
            except (ValueError, TypeError):
                two_min_count = 0
            
            # Vérifier la colonne Dis pour disqualifications
            # 'D' = Disqualification directe (1 carton rouge)
            # 'R' = Rapport/Exclusion définitive (1 carton rouge + 1 carton bleu)
            if 'disqualification' in col_indices:
                dis_val = str(row.iloc[col_indices['disqualification']]).strip().upper()
                if dis_val == 'D':
                    red_cards = 1
                elif dis_val == 'R':
                    red_cards = 1
                    blue_cards = 1
            
            player_data = {
                'team': team_name,
                'player_name': name_val,
                'is_official': is_official,
                'is_captain': is_captain,
                'goals': row.iloc[col_indices.get('goals', 10)] if 'goals' in col_indices else '',
                'shots': row.iloc[col_indices.get('shots', 12)] if 'shots' in col_indices else '',
                'goals_7m': row.iloc[col_indices.get('7m', 11)] if '7m' in col_indices else '',
                'yellow_cards': yellow_cards,
                'two_minutes': two_min_val,
                'red_cards': red_cards,
                'blue_cards': blue_cards,
                'saves': row.iloc[col_indices.get('saves', 13)] if 'saves' in col_indices else '',
            }
            players.append(player_data)
        
        return players
    
    # Extraire les joueurs des deux équipes
    if club_recevant_idx is not None:
        team1_name = df_raw.iloc[club_recevant_idx, 1] if len(df_raw.iloc[club_recevant_idx]) > 1 else "Equipe Recevante"
        players_team1 = extract_players_section(club_recevant_idx, club_visiteur_idx or len(df_raw), team1_name)
        all_players.extend(players_team1)
    
    if club_visiteur_idx is not None:
        team2_name = df_raw.iloc[club_visiteur_idx, 1] if len(df_raw.iloc[club_visiteur_idx]) > 1 else "Equipe Visiteuse"
        # Trouver la fin de la section visiteur (chercher "DETAIL" ou fin du dataframe)
        end_idx = len(df_raw)
        for idx in range(club_visiteur_idx + 1, len(df_raw)):
            if 'DETAIL' in str(df_raw.iloc[idx].values) or 'Déroulé' in str(df_raw.iloc[idx].values):
                end_idx = idx
                break
        
        players_team2 = extract_players_section(club_visiteur_idx, end_idx, team2_name)
        all_players.extend(players_team2)
    
    # Créer le DataFrame final
    df = pd.DataFrame(all_players)
    
    # Nettoyer et convertir les colonnes numériques
    for col in ['goals', 'shots', 'goals_7m', 'yellow_cards', 'two_minutes', 'red_cards', 'blue_cards', 'saves']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    return df

def extract_match_actions(pdf_path):
    # Lire toutes les pages
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    print("Tables trouvées:", len(tables))
    if len(tables) == 0:
        raise ValueError("Aucun tableau trouvé — vérifier le PDF ou le paramètre flavor")
        
    # Concaténer toutes les tables
    df_raw = pd.concat([t.df for t in tables], ignore_index=True)
    
    # Trouver la ligne qui contient "Déroulé du Match"
    deroul_idx = None
    for idx, row in df_raw.iterrows():
        row_str = ' '.join(row.astype(str).values)
        if 'Déroulé du Match' in row_str or 'Déroulé' in row_str:
            deroul_idx = idx
            break
    
    if deroul_idx is None:
        print("Section 'Déroulé du Match' non trouvée")
        return pd.DataFrame()
    
    print(f"Déroulé du Match trouvé à l'index: {deroul_idx}")
    
    # Extraire toutes les actions après "Déroulé du Match"
    actions = []
    
    for idx in range(deroul_idx + 1, len(df_raw)):
        row = df_raw.iloc[idx]
        
        # Colonnes typiques: Temps (col 0 ou 4), Score (col 1 ou 5), Action (col 2 ou 6/7)
        # On peut avoir les actions dans colonnes 0-2 ou 4-6
        
        # Extraire colonnes 0, 1, 2
        time_col0 = str(row.iloc[0]).strip()
        score_col0 = str(row.iloc[1]).strip()
        action_col0 = str(row.iloc[2]).strip() if len(row) > 2 else ""
        
        # Combiner colonnes 2 et 3 pour l'action si nécessaire
        if len(row) > 3:
            action_col0_extra = str(row.iloc[3]).strip()
            if action_col0_extra and action_col0_extra != 'nan' and not ':' in action_col0_extra:
                action_col0 = action_col0 + ' ' + action_col0_extra
        
        if time_col0 and time_col0 != 'nan' and time_col0 != 'Temps' and ':' in time_col0:
            # Nettoyer l'action (enlever les retours à la ligne)
            action_clean = action_col0.replace('\n', '').replace('\r', '').strip()
            if action_clean and action_clean != 'nan':  # Ne garder que les actions non vides
                # Déterminer la période en fonction du temps
                # Si temps > 30:00, c'est la période 2, sinon période 1
                try:
                    minutes = int(time_col0.split(':')[0])
                    period = 2 if minutes >= 30 else 1
                except:
                    period = 1  # Par défaut période 1 en cas d'erreur
                
                actions.append({
                    'period': period,
                    'time': time_col0,
                    'score': score_col0,
                    'action': action_clean
                })
        
        # Extraire colonnes 4, 5, 6/7
        if len(row) > 4:
            time_col4 = str(row.iloc[4]).strip()
            score_col4 = str(row.iloc[5]).strip()
            action_col4 = str(row.iloc[6]).strip() if len(row) > 6 else ""
            
            # Combiner colonnes 6 et 7 si nécessaire pour l'action
            if len(row) > 7:
                action_col4_extra = str(row.iloc[7]).strip()
                if action_col4_extra and action_col4_extra != 'nan':
                    action_col4 = action_col4 + ' ' + action_col4_extra
            
            if time_col4 and time_col4 != 'nan' and time_col4 != 'Temps' and ':' in time_col4:
                # Nettoyer l'action (enlever les retours à la ligne)
                action_clean = action_col4.replace('\n', '').replace('\r', '').strip()
                if action_clean and action_clean != 'nan':  # Ne garder que les actions non vides
                    # Déterminer la période en fonction du temps
                    # Si temps > 30:00, c'est la période 2, sinon période 1
                    try:
                        minutes = int(time_col4.split(':')[0])
                        period = 2 if minutes >= 30 else 1
                    except:
                        period = 1  # Par défaut période 1 en cas d'erreur
                    
                    actions.append({
                        'period': period,
                        'time': time_col4,
                        'score': score_col4,
                        'action': action_clean
                    })
    
    return pd.DataFrame(actions)

def parse_action_details(action_str):
    """
    Parse une chaîne d'action pour extraire le type d'action, l'équipe et le joueur.
    Exemples:
    - ButJRN°18JUQUELloic -> type: But, team: JR (Recevant), player_number: 18, player_name: JUQUEL loic
    - TirJVN°15MONIERalan -> type: Tir, team: JV (Visiteur), player_number: 15, player_name: MONIER alan
    - 2MNJRN°9FALANDRYsacha -> type: 2MN, team: JR, player_number: 9, player_name: FALANDRY sacha
    - AvertissementJRN°8KOVALEVSKYboris -> type: Avertissement, team: JR, player_number: 8, player_name: KOVALEVSKY boris
    - TempsMortd'EquipeVisiteur -> type: TempsMort, team: Visiteur
    - ProtocoleCommotionJRN°4RICHARDlouis -> type: ProtocoleCommotion, team: JR, player_number: 4, player_name: RICHARD louis
    """
    import re
    
    action_str = action_str.strip()
    
    # Types d'actions possibles
    action_types = {
        'But': 'Goal',
        'But7m': 'Goal_7m',
        'Tir': 'Shot',
        'Arrêt': 'Save',
        '2MN': 'Suspension_2min',
        'Avertissement': 'Warning',
        'TempsMortd\'Equipe': 'Timeout',
        'TempsMort': 'Timeout',
        'ProtocoleCommotion': 'Concussion_Protocol'
    }
    
    # Extraire le type d'action
    action_type = None
    action_type_raw = None
    for key in action_types.keys():
        if action_str.startswith(key):
            action_type = action_types[key]
            action_type_raw = key
            break
    
    # Si aucun type trouvé, retourner des valeurs par défaut
    if not action_type:
        return {
            'action_type': 'Unknown',
            'team': None,
            'player_number': None,
            'player_name': None
        }
    
    # Cas spécial: Timeout
    if 'Timeout' in action_type:
        team = 'Visiteur' if 'Visiteur' in action_str else 'Recevant' if 'Recevant' in action_str else None
        return {
            'action_type': action_type,
            'team': team,
            'player_number': None,
            'player_name': None
        }
    
    # Extraire l'équipe (JR = Joueur Recevant, JV = Joueur Visiteur, OV = Officiel Visiteur)
    team_match = re.search(r'(JR|JV|OV)', action_str)
    team = None
    if team_match:
        team_code = team_match.group(1)
        if team_code == 'JR':
            team = 'Home'
        elif team_code == 'JV':
            team = 'Away'
        elif team_code == 'OV':
            team = 'Away'  # Officiel visiteur
    
    # Extraire le numéro du joueur (N°XX)
    number_match = re.search(r'N°(\d+)', action_str)
    player_number = number_match.group(1) if number_match else None
    
    # Extraire le nom du joueur (tout ce qui suit N°XX)
    player_name = None
    if number_match:
        # Trouver l'index après N°XX
        name_start = action_str.find(number_match.group(0)) + len(number_match.group(0))
        player_name = action_str[name_start:].strip()
        
        # Nettoyer le nom (parfois il y a des caractères spéciaux)
        if player_name:
            # Séparer le nom en parties (NOM prénom)
            # Exemple: "JUQUELloic" -> "JUQUEL loic"
            # On cherche la première minuscule pour savoir où commence le prénom
            first_lower = None
            for i, char in enumerate(player_name):
                if char.islower():
                    first_lower = i
                    break
            
            if first_lower is not None:
                # Tout avant la première minuscule = nom de famille
                # Tout après = prénom
                last_name = player_name[:first_lower]
                first_name = player_name[first_lower:]
                player_name = f"{last_name} {first_name}"
    
    return {
        'action_type': action_type,
        'team': team,
        'player_number': player_number,
        'player_name': player_name
    }

def extract_match_info(pdf_path):
    """Extract match information including teams, scores, date, and league"""
    import re
    from datetime import datetime
    
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    df_raw = pd.concat([t.df for t in tables], ignore_index=True)
    
    # Find team names
    home_team = None
    away_team = None
    match_date = None
    league_name = None
    league_group_id = None
    league_group_name = None
    season = None
    ht_score_home = None
    ht_score_away = None
    final_score_home = None
    final_score_away = None
    
    # Extract team names, date, league from rows
    for idx, row in df_raw.iterrows():
        row_str = ' '.join(row.astype(str).values)
        if 'ClubRecevant' in row_str:
            # Team name is in column 1
            home_team = str(row.iloc[1]).strip()
        elif 'ClubVisiteur' in row_str:
            away_team = str(row.iloc[1]).strip()
        elif 'Compétition' in row_str or 'Competition' in row_str:
            # Extract league/competition name from the cell
            # The structure is: "+16 ANS M EXCELLENCE...\nCompétition\nGroupe\nM610001021\nPOULE C"
            cell_text = str(row.iloc[0])
            lines = cell_text.split('\n')
            
            # Parse the lines in order
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                # The competition name is the first line (before "Compétition")
                if i == 0 and line not in ['Compétition', 'Competition']:
                    league_name = line
                # Skip "Compétition" and "Groupe" labels
                elif line in ['Compétition', 'Competition', 'Groupe', 'Group']:
                    continue
                # Group ID starts with M followed by digits
                elif line.startswith('M') and len(line) > 1 and line[1:].isdigit():
                    league_group_id = line
                # Group name is everything else after group_id
                elif league_group_id and not league_group_name:
                    league_group_name = line
        elif 'Saison' in row_str or 'Season' in row_str:
            # Extract season (e.g., "2024-2025")
            for col_idx in range(1, len(row)):
                cell_text = str(row.iloc[col_idx]).strip()
                if cell_text and cell_text not in ['nan', 'Saison', 'Season']:
                    season = cell_text
                    break
        elif 'DATE:' in row_str or 'Journée / Date' in row_str:
            # Extract match date from the row
            cell_text = str(row.iloc[2]) if len(row) > 2 else row_str
            # Look for date pattern like "samedi 11/10/2025 21:00"
            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', cell_text)
            if date_match:
                date_str = date_match.group(1)
                # Parse date from DD/MM/YYYY format
                match_date = datetime.strptime(date_str, '%d/%m/%Y').date()
        elif 'DETAIL' in row_str and 'SCORE' in row_str:
            # Found the score section, extract scores from the cell
            score_text = str(row.iloc[0])
            lines = score_text.split('\n')
            
            # Extract only the numeric values (scores)
            scores = [line.strip() for line in lines if line.strip().isdigit()]
            
            # The pattern is: [ht_home, ht_away, final_home, final_away]
            # Because REC/VIS appear twice (for Période 1 and Fin Tps Reglem)
            # and the scores follow in that order
            if len(scores) >= 4:
                ht_score_home = int(scores[0])
                ht_score_away = int(scores[1])
                final_score_home = int(scores[2])
                final_score_away = int(scores[3])
    
    return {
        'home_team': home_team,
        'away_team': away_team,
        'match_date': match_date,
        'league_name': league_name,
        'league_group_id': league_group_id,
        'league_group_name': league_group_name,
        'season': season,
        'ht_score_home': ht_score_home,
        'ht_score_away': ht_score_away,
        'final_score_home': final_score_home,
        'final_score_away': final_score_away
    }

def create_match_in_db(match_info):
    """Create league, teams and match in database, return match_id and team IDs"""
    print("\n" + "="*50)
    print("Creating match in database...")
    
    # Get or create league
    league_id = None
    if match_info.get('league_name'):
        # Build query to find existing league
        query = supabase.table("leagues").select("*").eq("name", match_info['league_name'])
        
        # Add filters for group_id and season if available
        if match_info.get('league_group_id'):
            query = query.eq("group_id", match_info['league_group_id'])
        if match_info.get('season'):
            query = query.eq("season", match_info['season'])
        
        league_response = query.execute()
        
        if league_response.data:
            league_id = league_response.data[0]['id']
            group_info = f" - {match_info['league_group_name']}" if match_info.get('league_group_name') else ""
            print(f"✓ League '{match_info['league_name']}'{group_info} found (ID: {league_id})")
        else:
            # Create new league
            league_data = {"name": match_info['league_name']}
            if match_info.get('league_group_id'):
                league_data['group_id'] = match_info['league_group_id']
            if match_info.get('league_group_name'):
                league_data['group_name'] = match_info['league_group_name']
            if match_info.get('season'):
                league_data['season'] = match_info['season']
            
            league_response = supabase.table("leagues").insert(league_data).execute()
            league_id = league_response.data[0]['id']
            
            # Build display info
            group_info = f" - {match_info['league_group_name']}" if match_info.get('league_group_name') else ""
            season_info = f" (Season: {match_info['season']})" if match_info.get('season') else ""
            print(f"✓ League '{match_info['league_name']}'{group_info} created (ID: {league_id}){season_info}")
    
    # Get or create home team
    home_team_response = supabase.table("teams").select("*").eq("name", match_info['home_team']).execute()
    if home_team_response.data:
        home_team_id = home_team_response.data[0]['id']
        print(f"✓ Home team '{match_info['home_team']}' found (ID: {home_team_id})")
    else:
        home_team_response = supabase.table("teams").insert({"name": match_info['home_team']}).execute()
        home_team_id = home_team_response.data[0]['id']
        print(f"✓ Home team '{match_info['home_team']}' created (ID: {home_team_id})")
    
    # Get or create away team
    away_team_response = supabase.table("teams").select("*").eq("name", match_info['away_team']).execute()
    if away_team_response.data:
        away_team_id = away_team_response.data[0]['id']
        print(f"✓ Away team '{match_info['away_team']}' found (ID: {away_team_id})")
    else:
        away_team_response = supabase.table("teams").insert({"name": match_info['away_team']}).execute()
        away_team_id = away_team_response.data[0]['id']
        print(f"✓ Away team '{match_info['away_team']}' created (ID: {away_team_id})")
    
    # Check if match already exists (same teams and date)
    match_date_str = str(match_info['match_date']) if match_info['match_date'] else None
    existing_match = supabase.table("matches").select("*").eq("home_team_id", home_team_id).eq("away_team_id", away_team_id).eq("match_date", match_date_str).execute()
    
    if existing_match.data:
        # Match already exists
        match_id = existing_match.data[0]['id']
        print(f"⚠️  Match already exists (ID: {match_id})")
        print(f"  Date: {match_info['match_date']}")
        print(f"  {match_info['home_team']} vs {match_info['away_team']}")
        print(f"  Halftime: {existing_match.data[0]['ht_score_home']} - {existing_match.data[0]['ht_score_away']}")
        print(f"  Final: {existing_match.data[0]['final_score_home']} - {existing_match.data[0]['final_score_away']}")
        print(f"\n⛔ Aborting to prevent duplicate data. Delete the match first if you want to re-import.")
        return None, None, None, None, None
    
    # Create match
    match_data = {
        "league_id": league_id,
        "home_team_id": home_team_id,
        "away_team_id": away_team_id,
        "match_date": match_date_str,
        "ht_score_home": match_info['ht_score_home'],
        "ht_score_away": match_info['ht_score_away'],
        "final_score_home": match_info['final_score_home'],
        "final_score_away": match_info['final_score_away']
    }
    
    match_response = supabase.table("matches").insert(match_data).execute()
    match_id = match_response.data[0]['id']
    print(f"✓ Match created (ID: {match_id})")
    if match_info.get('league_name'):
        print(f"  League: {match_info['league_name']}")
    print(f"  Date: {match_info['match_date']}")
    print(f"  {match_info['home_team']} vs {match_info['away_team']}")
    print(f"  Halftime: {match_info['ht_score_home']} - {match_info['ht_score_away']}")
    print(f"  Final: {match_info['final_score_home']} - {match_info['final_score_away']}")
    
    return match_id, home_team_id, away_team_id, match_info['home_team'], match_info['away_team']

def upload_to_supabase(df_stats, df_actions, match_id, home_team_id, away_team_id, home_team_name, away_team_name):
    """Upload match stats and actions to Supabase"""
    print("\n" + "="*50)
    print("Uploading data to Supabase...")
    
    # Upload match stats
    print(f"Uploading {len(df_stats)} player records to 'player_stats' table...")
    stats_records = df_stats.to_dict('records')
    
    # Add match_id and team_id to each record
    for record in stats_records:
        # Convert NaN to None for JSON serialization
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
        
        # Add match_id
        record['match_id'] = match_id
        
        # Determine team_id based on team name
        team_name = record.get('team', '')
        if team_name == home_team_name:
            record['team_id'] = home_team_id
        elif team_name == away_team_name:
            record['team_id'] = away_team_id
        else:
            record['team_id'] = None
        
        # Rename 'team' to 'team_name' to match schema
        record['team_name'] = record.pop('team')
        
        # Get or create player record (only for non-officials)
        player_id = None
        if not record.get('is_official', False) and record['team_id'] is not None:
            player_name = record['player_name']
            
            # Check if player already exists
            existing_player = supabase.table("players").select("*").eq("name", player_name).eq("team_id", record['team_id']).execute()
            
            if existing_player.data:
                player_id = existing_player.data[0]['id']
            else:
                # Create new player
                player_data = {
                    "name": player_name,
                    "team_id": record['team_id']
                }
                new_player = supabase.table("players").insert(player_data).execute()
                player_id = new_player.data[0]['id']
        
        # Add player_id to the record
        record['player_id'] = player_id
    
    try:
        response_stats = supabase.table("player_stats").insert(stats_records).execute()
        print(f"✓ Successfully uploaded {len(stats_records)} player records")
    except Exception as e:
        print(f"✗ Error uploading player stats: {e}")
    
    # Upload match actions (if any)
    if not df_actions.empty:
        print(f"\nUploading {len(df_actions)} action records to 'actions' table...")
        actions_records = df_actions.to_dict('records')
        
        # Add match_id to each record and convert NaN to None
        for record in actions_records:
            # Add match_id
            record['match_id'] = match_id
            
            # Convert NaN to None for JSON serialization
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        
        try:
            response_actions = supabase.table("actions").insert(actions_records).execute()
            print(f"✓ Successfully uploaded {len(actions_records)} action records")
        except Exception as e:
            print(f"✗ Error uploading actions: {e}")
    else:
        print("\n⚠️  No actions to upload (actions section not found in PDF)")
    
    print("\n" + "="*50)
    print("Upload complete!")

# Main execution
if __name__ == "__main__":
    # Check for command-line argument
    if len(sys.argv) > 1:
        pdf_input = sys.argv[1]
        
        # Check if input is a URL
        if pdf_input.startswith('http://') or pdf_input.startswith('https://'):
            print("="*50)
            print(f"Processing PDF from URL: {pdf_input}")
            print("="*50)
            pdf_path = download_pdf(pdf_input)
            
            if pdf_path is None:
                print("Failed to download PDF. Exiting.")
                exit(1)
        else:
            # Assume it's a local file path
            pdf_path = pdf_input
            if not os.path.exists(pdf_path):
                print(f"Error: File '{pdf_path}' not found.")
                exit(1)
    else:
        # Default to match.pdf
        pdf_path = "match.pdf"
        if not os.path.exists(pdf_path):
            print("Error: No PDF specified and default 'match.pdf' not found.")
            print("\nUsage:")
            print("  python read-match.py <pdf_url_or_path>")
            print("\nExample:")
            print("  python read-match.py https://media-ffhb-fdm.ffhandball.fr/fdm/V/A/G/A/VAGAHYB.pdf")
            exit(1)
    
    # Step 1: Extract match information
    print("\n" + "="*50)
    print("STEP 1: Extracting match information...")
    match_info = extract_match_info(pdf_path)
    if match_info.get('league_name'):
        print(f"League: {match_info['league_name']}")
        if match_info.get('league_group_name'):
            print(f"Group: {match_info['league_group_name']} (ID: {match_info.get('league_group_id', 'N/A')})")
        if match_info.get('season'):
            print(f"Season: {match_info['season']}")
    print(f"Match Date: {match_info['match_date']}")
    print(f"Home Team: {match_info['home_team']}")
    print(f"Away Team: {match_info['away_team']}")
    print(f"Halftime Score: {match_info['ht_score_home']} - {match_info['ht_score_away']}")
    print(f"Final Score: {match_info['final_score_home']} - {match_info['final_score_away']}")
    
    # Step 2: Create match in database
    match_id, home_team_id, away_team_id, home_team_name, away_team_name = create_match_in_db(match_info)
    
    # Check if match creation was aborted due to duplicate
    if match_id is None:
        print("\n" + "="*50)
        print("Script aborted - match already exists in database")
        print("="*50)
        exit(0)
    
    # Step 3: Extract match stats
    print("\n" + "="*50)
    print("STEP 3: Extracting player statistics...")
    df_stats = extract_match_stats(pdf_path)
    print(df_stats)
    
    # Export to CSV
    df_stats.to_csv("match_stats.csv", index=False)
    print(f"\nData exported to match_stats.csv - {len(df_stats)} players found")
    
    # Step 4: Extract and export match actions
    print("\n" + "="*50)
    print("STEP 4: Extracting match actions...")
    df_actions = extract_match_actions(pdf_path)
    
    # Check if actions were found
    if df_actions.empty or 'action' not in df_actions.columns:
        print("⚠️  No match actions found in PDF - skipping action extraction")
        print("    The match will be uploaded with player stats only")
        df_actions = pd.DataFrame()  # Empty dataframe
    else:
        # Parse action details
        print("Parsing action details...")
        action_details = df_actions['action'].apply(parse_action_details)
        df_actions['action_type'] = action_details.apply(lambda x: x['action_type'])
        df_actions['team'] = action_details.apply(lambda x: x['team'])
        df_actions['player_number'] = action_details.apply(lambda x: x['player_number'])
        df_actions['player_name'] = action_details.apply(lambda x: x['player_name'])
        
        print(df_actions.head(20))
        df_actions.to_csv("match_actions.csv", index=False)
        print(f"\nActions exported to match_actions.csv - {len(df_actions)} actions found")
    
    # Step 5: Upload to Supabase
    print("\n" + "="*50)
    print("STEP 5: Uploading to Supabase...")
    upload_to_supabase(df_stats, df_actions, match_id, home_team_id, away_team_id, home_team_name, away_team_name)
    
    # Cleanup: Remove temporary PDF if it was downloaded
    if len(sys.argv) > 1 and (sys.argv[1].startswith('http://') or sys.argv[1].startswith('https://')):
        if os.path.exists("temp_match.pdf"):
            os.remove("temp_match.pdf")
            print("\n✓ Temporary PDF file cleaned up")

