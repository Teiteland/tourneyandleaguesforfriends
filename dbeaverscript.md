-- User table
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(200) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    is_locked BOOLEAN DEFAULT FALSE
);
-- Game table
CREATE TABLE IF NOT EXISTS game (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    platform VARCHAR(50),
    max_players INTEGER,
    allow_tournament BOOLEAN DEFAULT TRUE,
    allow_league BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE
);
-- Player table
CREATE TABLE IF NOT EXISTS player (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    is_dummy BOOLEAN DEFAULT FALSE
);
-- League table
CREATE TABLE IF NOT EXISTS league (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    game_id INTEGER REFERENCES game(id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    owner_id INTEGER REFERENCES "user"(id),
    unique_id VARCHAR(20)
);
-- LeagueRound table
CREATE TABLE IF NOT EXISTS league_round (
    id SERIAL PRIMARY KEY,
    league_id INTEGER REFERENCES league(id),
    round_number INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    is_completed BOOLEAN DEFAULT FALSE
);
-- Match table
CREATE TABLE IF NOT EXISTS match (
    id SERIAL PRIMARY KEY,
    league_id INTEGER REFERENCES league(id),
    round_id INTEGER REFERENCES league_round(id),
    home_player_id INTEGER REFERENCES player(id),
    away_player_id INTEGER REFERENCES player(id),
    home_track VARCHAR(100),
    away_track VARCHAR(100),
    home_score INTEGER,
    away_score INTEGER,
    is_draw BOOLEAN DEFAULT FALSE,
    is_walkover BOOLEAN DEFAULT FALSE,
    played_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'scheduled',
    walkover_winner INTEGER
);
-- Tournament table
CREATE TABLE IF NOT EXISTS tournament (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    game_id INTEGER REFERENCES game(id),
    owner_id INTEGER REFERENCES "user"(id),
    unique_id VARCHAR(20),
    format VARCHAR(20) DEFAULT 'single_elimination',
    best_of INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);
-- TournamentPlayer table
CREATE TABLE IF NOT EXISTS tournament_player (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournament(id),
    player_id INTEGER REFERENCES player(id),
    seed_number INTEGER,
    eliminated BOOLEAN DEFAULT FALSE,
    placement INTEGER
);
-- TournamentMatch table
CREATE TABLE IF NOT EXISTS tournament_match (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournament(id),
    bracket VARCHAR(20) DEFAULT 'winners',
    round_number INTEGER NOT NULL,
    match_number INTEGER NOT NULL,
    player1_id INTEGER REFERENCES player(id),
    player2_id INTEGER REFERENCES player(id),
    winner_id INTEGER REFERENCES player(id),
    score1 INTEGER,
    score2 INTEGER,
    is_bye BOOLEAN DEFAULT FALSE,
    next_match_id INTEGER REFERENCES tournament_match(id),
    loser_next_match_id INTEGER REFERENCES tournament_match(id),
    played_at TIMESTAMP
);
-- FFAMatch table
CREATE TABLE IF NOT EXISTS ffa_match (
    id SERIAL PRIMARY KEY,
    league_id INTEGER REFERENCES league(id),
    name VARCHAR(100) NOT NULL,
    game_id INTEGER REFERENCES game(id),
    owner_id INTEGER REFERENCES "user"(id),
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    played_at TIMESTAMP
);
-- FFAPlayer table
CREATE TABLE IF NOT EXISTS ffa_player (
    id SERIAL PRIMARY KEY,
    ffa_match_id INTEGER REFERENCES ffa_match(id),
    player_id INTEGER REFERENCES player(id),
    placement INTEGER,
    points_earned INTEGER DEFAULT 0
);

---
Deretter sett inn adminbruker:
INSERT INTO "user" (username, email, password_hash, is_admin)
VALUES ('Teiteland', 'even.teigland@gmail.com', 'scrypt:32768:8:1$X8J/Yc9YJPsD5C$YWJzcm90b2tlbi5hcHE=', TRUE)
ON CONFLICT (email) DO NOTHING;
(Merk: Passordet her må hashes - kan heller bare kjøre setningen under via appen etter tabeller er opprettet)
---