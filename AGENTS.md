# AGENTS.md - Gaming Tournament & League System

## Project Overview

- **Project Name:** Spillturnering og Liga
- **Type:** Web Application
- **Core Functionality:** Gaming league and tournament management system for competitive gaming
- **Target Users:** Gaming community members, tournament organizers, administrators

## Tech Stack

- **Backend:** Python 3.x + Flask
- **Database:** SQLite (architected for future migration)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Testing:** pytest
- **Configuration:** Environment variables (.env)

## Theme

- **Default:** Dark mode
- **Toggle:** Light mode and Earth mode available
- **Earth theme:** Warm whisky/brown color palette
- **CSS:** Plain CSS (no preprocessor)

## Project Structure

```
/app
  /routes          # Route handlers
  /models          # Database models
  /templates       # HTML templates
  /static          # CSS, JS, images
  /utils           # Helper functions
/config            # Configuration files
/tests             # Test files
.env               # Environment variables
```

## Phase 1: League System (Current)

### Features

1. **League/Serie Mode**
   - Round-robin format: all players play each other twice (home + away)
   - Home and away matches grouped in the same round
   - Configurable number of players (start: 12, max: 64)
   - Multiple parallel leagues/seasons
   - Owner or admin can end league manually even if not all matches played
   - Owner or admin can edit match results while league is active
   - Points system: 3 for win, 1 for draw, 0 for loss

2. **Match Scheduling**
   - Home player selects track (dropdown or manual entry)
   - Two legs per matchup: home and away (in same round)
   - Manual result entry with confirmation dialog
   - Round-based activation: rounds can be locked, active, or completed
   - Manual or automatic round progression
   - Walkover: owner/admin manually selects winner (3-0 default)
   - Cancel match: removes from statistics but keeps in log

3. **Player Management**
   - 12 auto-generated dummy players from Mario Kart universe on initialization
   - Player statistics tracked

4. **Owner System**
   - Any logged-in user can create a league
   - Creator becomes the league owner
   - Owner can: edit results, set walkover, cancel matches, activate/complete rounds, end league
   - Admin can manage ALL leagues
   - Owner transfer only via database

4. **Player Statistics**
   - Wins, Draws, Losses
   - Goals For, Goals Against
   - Series Won (leagues won as first place)
   - Favorite Opponent (most wins against single opponent)
   - Revenge Opportunity (last loss without subsequent win)
   - Next Matches (upcoming unplayed matches)

5. **History Tracking**
   - Per player history
   - Per tournament history
   - Per league round history
   - Per league history (all rounds for all players)

6. **User Authentication**
   - User registration with email and password
   - Password validation (8+ characters, letters and numbers)
   - Login with email and password
   - Account lockout after 5 failed login attempts
   - Admin can unlock locked accounts
   - Admin can reset user passwords
   - Users can change their own password
   - Admin account created via init-db

### Database Schema

#### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | User's display name |
| email | TEXT | User's email (unique) |
| password_hash | TEXT | Hashed password |
| is_admin | BOOLEAN | Admin privileges |
| created_at | DATETIME | Creation timestamp |
| failed_login_attempts | INTEGER | Failed login attempts |
| is_locked | BOOLEAN | Account locked status |

#### Games Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Game name |
| platform | TEXT | Gaming platform |
| is_active | BOOLEAN | Currently playable |

#### Players Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Player name |
| is_dummy | BOOLEAN | Auto-generated dummy player |

#### Leagues Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | League name |
| unique_id | TEXT | Unique identifier (12 chars) |
| game_id | INTEGER | Foreign key to Games |
| owner_id | INTEGER | Foreign key to Users (creator) |
| status | TEXT | active/completed/archived |
| created_at | DATETIME | Creation timestamp |
| ended_at | DATETIME | End timestamp |

#### LeagueRounds Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| league_id | INTEGER | Foreign key to Leagues |
| round_number | INTEGER | Round number |

#### Matches Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| league_id | INTEGER | Foreign key to Leagues |
| round_id | INTEGER | Foreign key to LeagueRounds |
| home_player_id | INTEGER | Foreign key to Players |
| away_player_id | INTEGER | Foreign key to Players |
| home_track | TEXT | Track chosen by home player |
| away_track | TEXT | Track chosen by away player |
| home_score | INTEGER | Home player score |
| away_score | INTEGER | Away player score |
| is_draw | BOOLEAN | Draw result |
| played_at | DATETIME | Match date |

### Auto-Generated Dummy Players (Mario Kart Universe)

1. Mario
2. Luigi
3. Peach
4. Daisy
5. Toad
6. Yoshi
7. Shy Guy
8. Donkey Kong
9. Wario
10. Waluigi
11. Bowser
12. Bowser Jr.

## Phase 2: Authentication (Implemented)

- User registration with email + password + confirm password
- Password hashing (bcrypt)
- Login with email + password
- Account lockout after 5 failed login attempts
- Admin can unlock accounts and reset passwords
- Users can change their own password

## Phase 3: Tournament System (Current)

### Features

1. **Tournament Creation**
   - Single elimination bracket
   - Double elimination with winners + losers bracket
   - Support for any number of players (auto-handles byes)
   - Recommended: 4, 8, 16, 32, 64 players
   - Grand finals: Best of 1 or Best of 3 (configurable by owner)
   - Owner system: creator + admin can manage

2. **Bracket Generation**
   - Automatic bye handling for odd player counts
   - Winners bracket (single elimination standard)
   - Losers bracket (double elimination)
   - Grand finals for double elimination

3. **Match Management**
   - Manual result entry
   - Automatic winner advancement
   - Loser moves to losers bracket (double elimination)
   - Tournament completion detection

### Database Schema

#### Tournament Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Tournament name |
| game_id | INTEGER | Foreign key to Games |
| owner_id | INTEGER | Foreign key to Users |
| unique_id | TEXT | Unique identifier (12 chars) |
| format | TEXT | single_elimination/double_elimination |
| best_of | INTEGER | 1 or 3 for grand finals |
| status | TEXT | draft/active/completed |
| created_at | DATETIME | Creation timestamp |
| started_at | DATETIME | Start timestamp |
| ended_at | DATETIME | End timestamp |

#### TournamentPlayer Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| tournament_id | INTEGER | Foreign key to Tournaments |
| player_id | INTEGER | Foreign key to Players |
| seed_number | INTEGER | Seed position |
| eliminated | BOOLEAN | Eliminated status |
| placement | INTEGER | Final placement |

#### TournamentMatch Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| tournament_id | INTEGER | Foreign key to Tournaments |
| bracket | TEXT | winners/losers/grand_finals |
| round_number | INTEGER | Round in bracket |
| match_number | INTEGER | Match within round |
| player1_id | INTEGER | Foreign key to Players |
| player2_id | INTEGER | Foreign key to Players |
| winner_id | INTEGER | Foreign key to Players |
| score1 | INTEGER | Player 1 score |
| score2 | INTEGER | Player 2 score |
| is_bye | BOOLEAN | Bye match |
| next_match_id | INTEGER | Next match (winner) |
| loser_next_match_id | INTEGER | Next match (loser) |
| played_at | DATETIME | Match timestamp |

## Phase 4: Extensibility (Future)

- Support for additional competitive games
- Configurable tournament formats
- Advanced statistics and analytics

## Development Guidelines

1. **Code Style:** Follow PEP 8
2. **Testing:** Write tests with pytest
3. **Security:** Never commit secrets, use .env for sensitive data
4. **Database:** Use migrations for schema changes
5. **Frontend:** Responsive design, dark mode default

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
PYTHONPATH=. pytest

# Start development server
flask run

# Initialize database (creates dummy players)
flask init-db

# Seed test data (creates leagues with matches for testing)
flask seed-data
```

## Environment Variables

```
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URI=sqlite:///gaming_liga.db
```
