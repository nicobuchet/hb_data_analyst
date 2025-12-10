-- SQL to create tables in Supabase for handball match data
-- Run this in Supabase SQL Editor

-- Drop existing tables to recreate them with proper structure
DROP TABLE IF EXISTS actions CASCADE;
DROP TABLE IF EXISTS player_stats CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS leagues CASCADE;

-- Table for leagues
CREATE TABLE leagues (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    group_id TEXT,
    group_name TEXT,
    season TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, group_id, season)
);

-- Table for teams
CREATE TABLE teams (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for players
CREATE TABLE players (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    team_id BIGINT REFERENCES teams(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, team_id)
);

-- Table for matches
CREATE TABLE matches (
    id BIGSERIAL PRIMARY KEY,
    league_id BIGINT REFERENCES leagues(id),
    home_team_id BIGINT REFERENCES teams(id),
    away_team_id BIGINT REFERENCES teams(id),
    match_date DATE,
    ht_score_home INTEGER,
    ht_score_away INTEGER,
    final_score_home INTEGER,
    final_score_away INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for player statistics
CREATE TABLE player_stats (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES matches(id) ON DELETE CASCADE,
    player_id BIGINT REFERENCES players(id),
    team_id BIGINT REFERENCES teams(id),
    team_name TEXT NOT NULL,
    player_name TEXT NOT NULL,
    is_official BOOLEAN DEFAULT FALSE,
    is_captain BOOLEAN DEFAULT FALSE,
    goals INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    goals_7m INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    two_minutes INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    blue_cards INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for match actions
CREATE TABLE actions (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES matches(id) ON DELETE CASCADE,
    period INTEGER NOT NULL,
    time TEXT NOT NULL,
    score TEXT,
    action TEXT,
    action_type TEXT,
    team TEXT,
    player_number TEXT,
    player_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_leagues_name ON leagues(name);
CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(name);
CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);
CREATE INDEX IF NOT EXISTS idx_players_team ON players(team_id);
CREATE INDEX IF NOT EXISTS idx_matches_league ON matches(league_id);
CREATE INDEX IF NOT EXISTS idx_matches_home_team ON matches(home_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_away_team ON matches(away_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_player_stats_match ON player_stats(match_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_player ON player_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_team ON player_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_team_name ON player_stats(team_name);
CREATE INDEX IF NOT EXISTS idx_player_stats_player_name ON player_stats(player_name);
CREATE INDEX IF NOT EXISTS idx_player_stats_is_official ON player_stats(is_official);
CREATE INDEX IF NOT EXISTS idx_actions_match ON actions(match_id);
CREATE INDEX IF NOT EXISTS idx_actions_period ON actions(period);
CREATE INDEX IF NOT EXISTS idx_actions_action_type ON actions(action_type);
CREATE INDEX IF NOT EXISTS idx_actions_team ON actions(team);
CREATE INDEX IF NOT EXISTS idx_actions_player_name ON actions(player_name);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE leagues ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE players ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE player_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE actions ENABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations (adjust based on your needs)
CREATE POLICY "Enable read access for all users" ON leagues FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON leagues FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON leagues FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON leagues FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON teams FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON teams FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON teams FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON teams FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON players FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON players FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON players FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON players FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON matches FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON matches FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON matches FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON matches FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON player_stats FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON player_stats FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON player_stats FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON player_stats FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON actions FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON actions FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON actions FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON actions FOR DELETE USING (true);

-- Display success message
DO $$ 
BEGIN
    RAISE NOTICE 'Tables created successfully!';
    RAISE NOTICE 'teams: stores team information';
    RAISE NOTICE 'matches: stores match information with home/away teams';
    RAISE NOTICE 'player_stats: stores player/official statistics linked to matches';
    RAISE NOTICE 'actions: stores chronological match actions linked to matches';
END $$;
