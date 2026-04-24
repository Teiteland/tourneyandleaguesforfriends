# Spillturnering og Liga

A gaming league and tournament management system for competitive gaming.

## Quick Start

```bash
# Clone and setup in one command
./setup.sh

# Create admin user (required after setup)
flask create-admin

# Start the server
flask run
```

The application will be available at `http://127.0.0.1:5000`

## Features

### Current Features (Phase 1-4)

- **League/Serie System** - Round-robin format where all players play each other twice (home + away) in the same round
- **Multiple Parallel Leagues** - Create and manage multiple active leagues simultaneously
- **Player Management** - Add/remove players to active leagues
- **Catch-up Round** - When adding players mid-league, matches are scheduled in remaining rounds, with any overflow placed in a final catch-up round (currently disabled)
- **Manual League End** - Owner or admin can end a league manually even if not all matches played
- **Edit Match Results** - Owner or admin can edit results while league is active (click on result to edit)
- **Round Activation** - Rounds can be locked, active, or completed
- **Automatic Round Progression** - Next round activates automatically when all active rounds are completed
- **Manual Round Control** - Owner or admin can manually activate or complete rounds
- **Walkover** - Owner or admin can set walkover (3-0) by selecting winner
- **Cancel Match** - Owner or admin can cancel matches (excluded from statistics but kept in log)
- **Points System** - 3 points for win, 1 point for draw, 0 points for loss
- **Match Scheduling** - Home player selects track (dropdown or manual entry)
- **History Tracking** - View history per player, tournament, league round, and overall league
- **Player Statistics** - Wins, Draws, Losses, Goals For/Against, Series Won, Favorite Opponent, Revenge Opportunity, Next Matches
- **Themes** - Dark mode (default), Light mode, and Earth mode (whisky/brown colors)
- **User Registration** - Users can register with email and password (8+ chars, letters + numbers)
- **Account Security** - Account lockout after 5 failed login attempts, admin can unlock
- **User Management** - Admin can view users, unlock accounts, and reset passwords
- **Profile** - Users can change their own password
- **Unit Tests** - Comprehensive test suite with pytest
- **Setup Script** - `./setup.sh` to initialize database and seed test data

### Tournament System (Phase 3)

- **Single Elimination** - Standard winner's bracket tournament
- **Double Elimination** - Winner’s bracket + Loser’s bracket with Grand Finals
- **Flexible Player Count** - Any number of players supported (auto-handles byes)
- **Recommended Sizes** - 4, 8, 16, 32, 64 players for best experience
- **Grand Finals** - Configurable: Best of 1 or Best of 3
- **Match Result Entry** - Manual score entry by owner/admin
- **Automatic Bracket Progression** - Winners advance, losers move to losers bracket (double elim)
- **Tournament Completion** - Automatic detection when champion is crowned
- **Owner System** - Tournament creator has management rights

### FFA System (Phase 4)

- **Standalone FFA** - Create FFA from main page or My Events
- **FFA in Leagues** - Add FFA rounds within leagues
- **Scoring** - 1st place gets floor(X/2) points, everyone else gets 1 point
- **Flexible Player Count** - Any number of players (minimum 2)
- **Owner System** - FFA creator has management rights

### Mass Start System (Phase 4b)

- **Standalone Mass Start** - Create Mass Start from main page or My Events
- **Mass Start in Leagues** - Add Mass Start rounds within leagues
- **Scoring** - 1st place gets X points, 2nd gets X-1, ..., last gets 1, "Not finished" gets 0
- **Flexible Player Count** - Any number of players (minimum 2)
- **Owner System** - Creator has management rights

### Upcoming Features (Phase 5+)

- Support for additional competitive games
- Advanced statistics and analytics

## Requirements

- Python 3.x
- SQLite

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root (copy from `.env.example` if available)
4. Initialize the database and migrations:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
5. Create admin user:
   ```bash
   flask create-admin
   ```
   Default admin: `Teiteland` / `admin123` (change password after first login)
6. (Optional) Seed test data:
   ```bash
   flask seed-data
   ```
7. Run the development server:
   ```bash
   flask run
   ```

## Database Migrations

When you make changes to the database models, you need to create and apply migrations:

1. **Create a migration** (after changing models):
   ```bash
   flask db migrate -m "Description of changes"
   ```

2. **Apply migrations** (to update the database):
   ```bash
   flask db upgrade
   ```

3. **Rollback** (if something goes wrong):
   ```bash
   flask db downgrade
   ```

4. **Check current migration status**:
   ```bash
   flask db current
   ```

**Important:** Never edit the migration files manually unless you know what you're doing. Let Flask-Migrate generate them automatically.

## Admin Access

To grant admin privileges to a user, run:
```bash
python -c "
from app import create_app
from app.models.models import db, User
app = create_app()
with app.app_context():
    user = User.query.filter_by(username='USERNAME').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f'{user.username} is now admin!')
"
```
Replace `USERNAME` with the actual username.

## League Owner System

Users who create a league become the "owner" of that league. Owners can:
- Edit match results
- Cancel matches
- Set walkover results
- Activate and complete rounds
- End the league

This is in addition to regular user capabilities. Admins can manage ALL leagues, while owners can only manage their own leagues.

### Transferring League Ownership

To transfer ownership of a league to another user, run:
```bash
python -c "
from app import create_app
from app.models.models import db, League, User
app = create_app()
with app.app_context():
    league = League.query.get(LEAGUE_ID)
    new_owner = User.query.filter_by(username='USERNAME').first()
    if league and new_owner:
        league.owner_id = new_owner.id
        db.session.commit()
        print(f'Ownership transferred to {new_owner.username}')
"
```
Replace `LEAGUE_ID` with the league's database ID and `USERNAME` with the new owner's username.

## Testing

```bash
# Run all tests
PYTHONPATH=. pytest

# Run specific test file
PYTHONPATH=. pytest tests/test_player_stats.py
```

## Usage

### Starting the Application

```bash
flask run
```

The application will be available at `http://127.0.0.1:5000`

### Creating a League

1. Log in as admin
2. Navigate to the leagues section
3. Create a new league with desired settings
4. Add players to the league
5. The system will automatically generate match schedule

### Recording Match Results

1. Navigate to the match
2. Enter the scores for both players
3. Submit the result

### Viewing History

- **Player History**: View individual player statistics and match history
- **League History**: View all rounds and matches for a specific league
- **Round History**: View matches in a specific round

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite / PostgreSQL (on Render)
- **Frontend**: HTML, CSS, JavaScript

## Deployment (Render)

### Quick Deploy

1. Push to GitHub
2. Create Web Service on [Render.com](https://render.com)
3. Connect your GitHub repository
4. Choose "Free" tier
5. Set Environment Variables:
   - `SECRET_KEY` = (generate random string, e.g. `openssl rand -hex 32`)
   - `DATABASE_URI` = (leave empty - Render provides PostgreSQL automatically)
6. Build Command: `pip install -r requirements.txt`
7. Start Command: `gunicorn -b :$PORT "app:create_app()"`

### Auto-Init

The Procfile automatically runs on each deploy:
- `flask create-admin` - Creates admin user (even.teigland@gmail.com / admin123)
- `flask seed-data` - Adds test data

### Updating

When you push new code to GitHub, Render automatically deploys. If you add new database models, run:

```bash
flask db migrate -m "description"
flask db upgrade
```

## License

[License information]
