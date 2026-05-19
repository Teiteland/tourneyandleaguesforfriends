# Spillturnering og Liga

A gaming league and tournament management system for competitive gaming.

## Quick Start

```bash
pip install -r requirements.txt
flask run
```

The application will be available at `http://127.0.0.1:5000`

## Features

### League/Serie System
- **Two formats**: Round Robin (1v1) and Free For All (FFA)
- **Round Robin**: all players play each other twice (home + away)
- **FFA League**: each round is a FFA match with linear scoring
- **Round Activation**: rounds can be locked, active, or completed
- **Automatic Progression**: next round activates when all matches complete
- **Manual Control**: owner/admin can manually activate/complete rounds
- **Multiple Parallel Leagues**: create and manage multiple leagues simultaneously
- **Match Management**: edit results, walkover (3-0), cancel match
- **Points System**: 3 for win, 1 for draw, 0 for loss (round-robin)
- **Auto-generated dummy players** from Mario Kart universe

### Tournament System
- **Single Elimination** - Standard winner's bracket
- **Double Elimination** - Winner's + Loser's bracket with Grand Finals
- **Flexible Player Count** - Any number supported (auto-handles byes)
- **Grand Finals** - Configurable: Best of 1 or Best of 3
- **Automatic Progression** - Winners advance, losers move to losers bracket

### FFA (Free For All)
- **Standalone FFA** from quick-links or Profile
- **FFA in Leagues** as multi-round FFA league
- **Linear scoring**: 1st = X points, 2nd = X-1, ..., last = 1 point
- **Flexible Player Count** - Any number (minimum 2)

### Mass Start
- **Standalone or within leagues**
- **Linear scoring**: same as FFA, with "Not finished" = 0 points
- **Flexible Player Count** - Any number (minimum 2)

### Player Selection
- **Autocomplete search**: search players by name (case-insensitive, after 2 chars)
- Players page shows only players you have played with/against (admin sees all)

### User System
- **Registration** with email + password (8+ chars, letters + numbers)
- **Account lockout** after 5 failed login attempts (admin can unlock)
- **Password change** from Profile page

### Navigation / Auth
- All pages except Home require login
- Nav bar: Home, Players, My Profile, Logout
- My Profile page includes: profile info, theme selector, password change, My Events summary

### Themes
- Dark mode (default), Light mode, Earth mode (whisky/brown colors)

### Player Statistics
- Wins, Draws, Losses, Goals For/Against
- Series Won, Favorite Opponent, Revenge Opportunity, Next Matches

### History Tracking
- Per player, per tournament, per league round, per league

## Requirements

- Python 3.x
- SQLite

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root:
   ```
   FLASK_APP=app
   SECRET_KEY=generate-a-random-secret
   DATABASE_URI=sqlite:///gaming_liga.db
   ```
4. Initialize the database:
   ```bash
   flask db upgrade
   flask init-db
   ```
5. Create admin user:
   ```bash
   flask create-admin
   ```
6. (Optional) Seed test data:
   ```bash
   flask seed-data
   ```
7. Run the development server:
   ```bash
   flask run
   ```

## Database Migrations

When you make changes to the database models:

1. **Create a migration**:
   ```bash
   flask db migrate -m "Description of changes"
   ```

2. **Apply migrations**:
   ```bash
   flask db upgrade
   ```

3. **Rollback**:
   ```bash
   flask db downgrade
   ```

## Admin Access

To grant admin privileges to a user:
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

## Testing

```bash
# Run all tests
PYTHONPATH=. pytest

# Run specific test file
PYTHONPATH=. pytest tests/test_player_stats.py
```

## Deployment

### Server Setup
- **Platform**: Home server with Cloudflare Tunnel (no port forwarding)
- **Process Manager**: systemd service (`tourney.service`)
- **Web Server**: gunicorn
- **Database**: SQLite (`gaming_liga.db`)

### Auto-Deploy
- GitHub webhook at `/webhook` with HMAC-SHA256 verification
- Webhook triggers `deploy.sh` which:
  1. `git pull origin main`
  2. `pip install -r requirements.txt`
  3. `flask db upgrade`
  4. `sudo systemctl restart tourney`

### Environment Variables (server .env)
```
FLASK_APP=app
SECRET_KEY=your-secret-key
DATABASE_URI=sqlite:///gaming_liga.db
WEBHOOK_SECRET=your-webhook-secret
```

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, Vanilla JavaScript

## License

[License information]
