-- PROMETHEUS V7 - SUPABASE SCHEMA (Simplified)
-- Execute in Supabase SQL Editor

-- 1. TOURNAMENTS
CREATE TABLE IF NOT EXISTS tournaments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tier INTEGER DEFAULT 1,
    prize_pool INTEGER DEFAULT 0,
    start_date DATE,
    end_date DATE,
    location TEXT,
    format JSONB DEFAULT '{}',
    status TEXT DEFAULT 'upcoming',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. TEAMS
CREATE TABLE IF NOT EXISTS teams (
    team_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    tag TEXT,
    region TEXT,
    tier TEXT DEFAULT 'C',
    logo_url TEXT,
    rating NUMERIC(10, 2) DEFAULT 0,
    all_time_wins INTEGER DEFAULT 0,
    all_time_losses INTEGER DEFAULT 0,
    last_match_time BIGINT,
    opendota_synced BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. PLAYERS
CREATE TABLE IF NOT EXISTS players (
    account_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    team_id BIGINT REFERENCES teams(team_id) ON DELETE SET NULL,
    role TEXT,
    position INTEGER,
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    winrate NUMERIC(5, 2) DEFAULT 0,
    is_current_team_member BOOLEAN DEFAULT TRUE,
    country_code TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. MATCHES
CREATE TABLE IF NOT EXISTS matches (
    match_id BIGINT PRIMARY KEY,
    team_id BIGINT REFERENCES teams(team_id) ON DELETE CASCADE,
    opponent_team_id BIGINT,
    opponent_name TEXT,
    radiant BOOLEAN,
    radiant_win BOOLEAN,
    won BOOLEAN,
    duration INTEGER,
    duration_min NUMERIC(5, 1),
    start_time BIGINT,
    match_date DATE,
    league_id BIGINT,
    league_name TEXT,
    game_mode INTEGER,
    cluster INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. TOURNAMENT_TEAMS
CREATE TABLE IF NOT EXISTS tournament_teams (
    tournament_id TEXT REFERENCES tournaments(id) ON DELETE CASCADE,
    team_id BIGINT REFERENCES teams(team_id) ON DELETE CASCADE,
    seed TEXT,
    ranking INTEGER,
    group_name TEXT,
    PRIMARY KEY (tournament_id, team_id)
);

-- 6. SCHEDULE
CREATE TABLE IF NOT EXISTS schedule (
    id SERIAL PRIMARY KEY,
    tournament_id TEXT REFERENCES tournaments(id) ON DELETE CASCADE,
    round TEXT NOT NULL,
    match_number INTEGER,
    match_date DATE,
    time_cet TIME,
    time_brt TIME,
    team_a_id BIGINT,
    team_b_id BIGINT,
    team_a_name TEXT,
    team_b_name TEXT,
    format TEXT DEFAULT 'Bo3',
    status TEXT DEFAULT 'scheduled',
    result JSONB DEFAULT '{}',
    stream_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. BETS
CREATE TABLE IF NOT EXISTS bets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT DEFAULT 'default_user',
    schedule_id INTEGER REFERENCES schedule(id) ON DELETE SET NULL,
    match_id BIGINT,
    tournament_id TEXT,
    team_a TEXT,
    team_b TEXT,
    selection TEXT NOT NULL,
    market TEXT DEFAULT 'match_winner',
    odds NUMERIC(5, 2) NOT NULL,
    stake NUMERIC(10, 2) NOT NULL,
    potential_return NUMERIC(10, 2),
    status TEXT DEFAULT 'pending',
    result TEXT,
    profit NUMERIC(10, 2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    settled_at TIMESTAMPTZ
);

-- 8. TEAM_STATS
CREATE TABLE IF NOT EXISTS team_stats (
    id SERIAL PRIMARY KEY,
    team_id BIGINT REFERENCES teams(team_id) ON DELETE CASCADE,
    period TEXT DEFAULT 'all_time',
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    winrate NUMERIC(5, 2) DEFAULT 0,
    avg_duration_min NUMERIC(5, 1) DEFAULT 0,
    radiant_winrate NUMERIC(5, 2) DEFAULT 0,
    dire_winrate NUMERIC(5, 2) DEFAULT 0,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(team_id, period)
);

-- 9. HEROES (Reference)
CREATE TABLE IF NOT EXISTS heroes (
    hero_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    localized_name TEXT,
    primary_attr TEXT,
    attack_type TEXT,
    roles TEXT[],
    img_url TEXT
);

-- 10. TEAM_HEROES
CREATE TABLE IF NOT EXISTS team_heroes (
    id SERIAL PRIMARY KEY,
    team_id BIGINT REFERENCES teams(team_id) ON DELETE CASCADE,
    hero_id INTEGER,
    games INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    winrate NUMERIC(5, 2) DEFAULT 0,
    UNIQUE(team_id, hero_id)
);

-- 11. BANKROLL
CREATE TABLE IF NOT EXISTS bankroll (
    id SERIAL PRIMARY KEY,
    user_id TEXT DEFAULT 'default_user' UNIQUE,
    balance NUMERIC(12, 2) DEFAULT 1000.00,
    initial_balance NUMERIC(12, 2) DEFAULT 1000.00,
    total_deposited NUMERIC(12, 2) DEFAULT 0,
    total_withdrawn NUMERIC(12, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. AUDIT_LOG
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    record_id TEXT,
    old_data JSONB,
    new_data JSONB,
    user_id TEXT DEFAULT 'system',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_teams_rating ON teams(rating DESC);
CREATE INDEX IF NOT EXISTS idx_players_team ON players(team_id);
CREATE INDEX IF NOT EXISTS idx_matches_team ON matches(team_id);
CREATE INDEX IF NOT EXISTS idx_bets_user ON bets(user_id);
CREATE INDEX IF NOT EXISTS idx_schedule_tournament ON schedule(tournament_id);

-- INSERT DEFAULT BANKROLL
INSERT INTO bankroll (user_id, balance, initial_balance)
VALUES ('default_user', 1000.00, 1000.00)
ON CONFLICT (user_id) DO NOTHING;
