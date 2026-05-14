-- =============================================================================
-- PROMETHEUS V7 - EXPANDED SCHEMA FOR 2025 MATCH DATA
-- 25,672 matches | 283,120 player records | 604,599 picks/bans
-- =============================================================================

-- =============================================================================
-- 1. MATCHES_2025 - Core match data (25,672 rows expected)
-- =============================================================================
CREATE TABLE IF NOT EXISTS matches_2025 (
    match_id BIGINT PRIMARY KEY,
    leagueid INTEGER,
    start_date_time TIMESTAMPTZ,
    duration INTEGER,
    cluster INTEGER,
    radiant_win BOOLEAN,
    
    -- Scores
    radiant_score INTEGER DEFAULT 0,
    dire_score INTEGER DEFAULT 0,
    
    -- Teams
    radiant_team_id BIGINT,
    dire_team_id BIGINT,
    radiant_team_name TEXT,
    dire_team_name TEXT,
    
    -- Game info
    game_mode INTEGER,
    lobby_type INTEGER,
    patch INTEGER,
    region INTEGER,
    
    -- Tower/Barracks status (bitmasks)
    tower_status_radiant INTEGER,
    tower_status_dire INTEGER,
    barracks_status_radiant INTEGER,
    barracks_status_dire INTEGER,
    
    -- First blood
    first_blood_time INTEGER,
    
    -- Series info
    series_id INTEGER,
    series_type INTEGER,
    
    -- Analysis metrics
    stomp NUMERIC,
    comeback NUMERIC,
    throw NUMERIC,
    loss NUMERIC,
    
    -- Replay
    replay_url TEXT,
    replay_salt BIGINT,
    
    -- Metadata
    month TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_matches_2025_date ON matches_2025(start_date_time DESC);
CREATE INDEX idx_matches_2025_league ON matches_2025(leagueid);
CREATE INDEX idx_matches_2025_radiant_team ON matches_2025(radiant_team_id);
CREATE INDEX idx_matches_2025_dire_team ON matches_2025(dire_team_id);
CREATE INDEX idx_matches_2025_month ON matches_2025(month);

-- =============================================================================
-- 2. MATCH_PLAYERS_2025 - Player performance per match (283,120 rows expected)
-- =============================================================================
CREATE TABLE IF NOT EXISTS match_players_2025 (
    id SERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL,
    account_id BIGINT,
    player_slot INTEGER,
    hero_id INTEGER,
    
    -- Core stats
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    
    -- Economy
    last_hits INTEGER DEFAULT 0,
    denies INTEGER DEFAULT 0,
    gold_per_min INTEGER DEFAULT 0,
    xp_per_min INTEGER DEFAULT 0,
    net_worth INTEGER DEFAULT 0,
    
    -- Damage
    hero_damage INTEGER DEFAULT 0,
    tower_damage INTEGER DEFAULT 0,
    hero_healing INTEGER DEFAULT 0,
    
    -- Items (6 slots + backpack + neutral)
    item_0 INTEGER,
    item_1 INTEGER,
    item_2 INTEGER,
    item_3 INTEGER,
    item_4 INTEGER,
    item_5 INTEGER,
    backpack_0 INTEGER,
    backpack_1 INTEGER,
    backpack_2 INTEGER,
    item_neutral INTEGER,
    
    -- Advanced stats
    level INTEGER,
    lane INTEGER,
    lane_role INTEGER,
    is_roaming BOOLEAN,
    
    -- Aggregated
    total_gold INTEGER,
    total_xp INTEGER,
    kda NUMERIC(5,2),
    
    -- Metadata
    leagueid INTEGER,
    month TEXT,
    
    UNIQUE(match_id, player_slot)
);

CREATE INDEX idx_mp2025_match ON match_players_2025(match_id);
CREATE INDEX idx_mp2025_account ON match_players_2025(account_id);
CREATE INDEX idx_mp2025_hero ON match_players_2025(hero_id);
CREATE INDEX idx_mp2025_month ON match_players_2025(month);

-- =============================================================================
-- 3. PICKS_BANS_2025 - Draft data (604,599 rows expected)
-- =============================================================================
CREATE TABLE IF NOT EXISTS picks_bans_2025 (
    id SERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL,
    leagueid INTEGER,
    
    is_pick BOOLEAN NOT NULL,
    hero_id INTEGER NOT NULL,
    team INTEGER NOT NULL,  -- 0=Radiant, 1=Dire
    "order" INTEGER NOT NULL,
    
    -- Metadata
    month TEXT,
    
    UNIQUE(match_id, "order")
);

CREATE INDEX idx_pb2025_match ON picks_bans_2025(match_id);
CREATE INDEX idx_pb2025_hero ON picks_bans_2025(hero_id);
CREATE INDEX idx_pb2025_pick ON picks_bans_2025(is_pick);
CREATE INDEX idx_pb2025_month ON picks_bans_2025(month);

-- =============================================================================
-- 4. OBJECTIVES_2025 - Game events (529,806 rows expected)
-- =============================================================================
CREATE TABLE IF NOT EXISTS objectives_2025 (
    id SERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL,
    leagueid INTEGER,
    
    time INTEGER NOT NULL,
    type TEXT NOT NULL,
    
    -- Event details
    team INTEGER,
    slot INTEGER,
    player_slot INTEGER,
    key TEXT,
    unit TEXT,
    value NUMERIC,
    killer INTEGER,
    
    -- Metadata
    month TEXT
);

CREATE INDEX idx_obj2025_match ON objectives_2025(match_id);
CREATE INDEX idx_obj2025_type ON objectives_2025(type);
CREATE INDEX idx_obj2025_time ON objectives_2025(time);
CREATE INDEX idx_obj2025_month ON objectives_2025(month);

-- =============================================================================
-- 5. TEAMFIGHTS_2025 - Team fight data (210,446 rows expected)
-- =============================================================================
CREATE TABLE IF NOT EXISTS teamfights_2025 (
    id SERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL,
    leagueid INTEGER,
    
    start_time INTEGER NOT NULL,
    end_time INTEGER NOT NULL,
    last_death INTEGER,
    deaths INTEGER DEFAULT 0,
    
    -- Metadata
    month TEXT
);

CREATE INDEX idx_tf2025_match ON teamfights_2025(match_id);
CREATE INDEX idx_tf2025_time ON teamfights_2025(start_time);
CREATE INDEX idx_tf2025_month ON teamfights_2025(month);

-- =============================================================================
-- 6. TEAMFIGHT_PLAYERS_2025 - Individual performance in teamfights
-- =============================================================================
CREATE TABLE IF NOT EXISTS teamfight_players_2025 (
    id SERIAL PRIMARY KEY,
    teamfight_id INTEGER REFERENCES teamfights_2025(id) ON DELETE CASCADE,
    match_id BIGINT NOT NULL,
    player_index INTEGER NOT NULL,  -- 0-9
    
    deaths INTEGER DEFAULT 0,
    buybacks INTEGER DEFAULT 0,
    damage INTEGER DEFAULT 0,
    healing INTEGER DEFAULT 0,
    gold_delta INTEGER DEFAULT 0,
    xp_delta INTEGER DEFAULT 0,
    xp_start INTEGER,
    xp_end INTEGER,
    
    -- JSON fields for detailed data
    ability_uses JSONB,
    item_uses JSONB,
    killed JSONB,
    deaths_pos JSONB,
    
    -- Metadata
    month TEXT
);

CREATE INDEX idx_tfp2025_teamfight ON teamfight_players_2025(teamfight_id);
CREATE INDEX idx_tfp2025_match ON teamfight_players_2025(match_id);
CREATE INDEX idx_tfp2025_month ON teamfight_players_2025(month);

-- =============================================================================
-- 7. MATCH_GRAPHS_2025 - Gold/XP advantage over time
-- =============================================================================
CREATE TABLE IF NOT EXISTS match_graphs_2025 (
    id SERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL,
    minute INTEGER NOT NULL,
    
    radiant_gold_adv INTEGER,
    radiant_xp_adv INTEGER,
    
    -- Metadata
    month TEXT,
    
    UNIQUE(match_id, minute)
);

CREATE INDEX idx_mg2025_match ON match_graphs_2025(match_id);

-- =============================================================================
-- 8. LEAGUES - Tournament/League reference
-- =============================================================================
CREATE TABLE IF NOT EXISTS leagues (
    leagueid INTEGER PRIMARY KEY,
    name TEXT,
    tier INTEGER,
    region TEXT,
    prize_pool INTEGER,
    start_date DATE,
    end_date DATE,
    
    -- Stats
    total_matches INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- 9. HEROES - Hero reference table
-- =============================================================================
CREATE TABLE IF NOT EXISTS heroes (
    hero_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    localized_name TEXT,
    primary_attr TEXT,
    attack_type TEXT,
    roles TEXT[],
    
    -- Base stats
    base_health INTEGER,
    base_mana INTEGER,
    base_armor NUMERIC,
    base_attack_min INTEGER,
    base_attack_max INTEGER,
    
    img_url TEXT
);

-- =============================================================================
-- 10. ITEMS - Item reference table  
-- =============================================================================
CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    localized_name TEXT,
    cost INTEGER,
    
    -- Classification
    is_recipe BOOLEAN DEFAULT FALSE,
    is_consumable BOOLEAN DEFAULT FALSE,
    is_neutral BOOLEAN DEFAULT FALSE,
    tier INTEGER,  -- For neutral items
    
    img_url TEXT
);

-- =============================================================================
-- ANALYTICAL VIEWS
-- =============================================================================

-- View: Hero pick/ban rates
CREATE OR REPLACE VIEW v_hero_meta_2025 AS
SELECT 
    hero_id,
    COUNT(*) FILTER (WHERE is_pick = true) as picks,
    COUNT(*) FILTER (WHERE is_pick = false) as bans,
    COUNT(*) as total_draft_appearances,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_pick = true) / NULLIF(COUNT(*), 0), 2) as pick_rate
FROM picks_bans_2025
GROUP BY hero_id
ORDER BY total_draft_appearances DESC;

-- View: Hero win rates
CREATE OR REPLACE VIEW v_hero_winrates_2025 AS
SELECT 
    mp.hero_id,
    COUNT(*) as games,
    COUNT(*) FILTER (WHERE 
        (mp.player_slot < 128 AND m.radiant_win = true) OR
        (mp.player_slot >= 128 AND m.radiant_win = false)
    ) as wins,
    ROUND(100.0 * COUNT(*) FILTER (WHERE 
        (mp.player_slot < 128 AND m.radiant_win = true) OR
        (mp.player_slot >= 128 AND m.radiant_win = false)
    ) / NULLIF(COUNT(*), 0), 2) as winrate,
    ROUND(AVG(mp.kills), 2) as avg_kills,
    ROUND(AVG(mp.deaths), 2) as avg_deaths,
    ROUND(AVG(mp.assists), 2) as avg_assists,
    ROUND(AVG(mp.gold_per_min), 0) as avg_gpm,
    ROUND(AVG(mp.xp_per_min), 0) as avg_xpm
FROM match_players_2025 mp
JOIN matches_2025 m ON mp.match_id = m.match_id
GROUP BY mp.hero_id
HAVING COUNT(*) >= 10
ORDER BY games DESC;

-- View: Team performance
CREATE OR REPLACE VIEW v_team_performance_2025 AS
SELECT 
    team_id,
    team_name,
    SUM(games) as total_games,
    SUM(wins) as total_wins,
    ROUND(100.0 * SUM(wins) / NULLIF(SUM(games), 0), 2) as winrate,
    ROUND(AVG(avg_duration), 0) as avg_duration
FROM (
    -- Radiant games
    SELECT 
        radiant_team_id as team_id,
        radiant_team_name as team_name,
        COUNT(*) as games,
        COUNT(*) FILTER (WHERE radiant_win = true) as wins,
        AVG(duration) as avg_duration
    FROM matches_2025
    WHERE radiant_team_id IS NOT NULL
    GROUP BY radiant_team_id, radiant_team_name
    
    UNION ALL
    
    -- Dire games
    SELECT 
        dire_team_id as team_id,
        dire_team_name as team_name,
        COUNT(*) as games,
        COUNT(*) FILTER (WHERE radiant_win = false) as wins,
        AVG(duration) as avg_duration
    FROM matches_2025
    WHERE dire_team_id IS NOT NULL
    GROUP BY dire_team_id, dire_team_name
) combined
GROUP BY team_id, team_name
HAVING SUM(games) >= 5
ORDER BY total_games DESC;

-- View: Monthly statistics
CREATE OR REPLACE VIEW v_monthly_stats_2025 AS
SELECT 
    month,
    COUNT(DISTINCT match_id) as matches,
    COUNT(*) FILTER (WHERE radiant_win = true) as radiant_wins,
    COUNT(*) FILTER (WHERE radiant_win = false) as dire_wins,
    ROUND(100.0 * COUNT(*) FILTER (WHERE radiant_win = true) / NULLIF(COUNT(*), 0), 2) as radiant_winrate,
    ROUND(AVG(duration) / 60.0, 1) as avg_duration_min,
    ROUND(AVG(radiant_score + dire_score), 1) as avg_total_kills
FROM matches_2025
GROUP BY month
ORDER BY month;

-- View: First blood statistics
CREATE OR REPLACE VIEW v_first_blood_stats AS
SELECT 
    CASE 
        WHEN first_blood_time < 60 THEN '0-1 min'
        WHEN first_blood_time < 120 THEN '1-2 min'
        WHEN first_blood_time < 180 THEN '2-3 min'
        WHEN first_blood_time < 300 THEN '3-5 min'
        ELSE '5+ min'
    END as fb_timing,
    COUNT(*) as matches,
    ROUND(100.0 * COUNT(*) FILTER (WHERE radiant_win = true) / NULLIF(COUNT(*), 0), 2) as radiant_winrate
FROM matches_2025
WHERE first_blood_time IS NOT NULL
GROUP BY 1
ORDER BY MIN(first_blood_time);

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Function to calculate KDA
CREATE OR REPLACE FUNCTION calculate_kda(kills INT, deaths INT, assists INT)
RETURNS NUMERIC AS $$
BEGIN
    IF deaths = 0 THEN
        RETURN kills + assists;
    ELSE
        RETURN ROUND((kills + assists)::NUMERIC / deaths, 2);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- GRANTS (for Supabase)
-- =============================================================================
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT SELECT ON v_hero_meta_2025 TO anon;
GRANT SELECT ON v_hero_winrates_2025 TO anon;
GRANT SELECT ON v_team_performance_2025 TO anon;
GRANT SELECT ON v_monthly_stats_2025 TO anon;
GRANT SELECT ON v_first_blood_stats TO anon;
