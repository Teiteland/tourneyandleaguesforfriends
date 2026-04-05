# Spillturnering og Liga

A gaming league and tournament management system for competitive gaming.

## Features

### Current Features (Phase 1)

- **League/Serie System** - Round-robin format where all players play each other twice (home + away)
- **Multiple Parallel Leagues** - Create and manage multiple active leagues simultaneously
- **Manual League End** - Admin can end a league manually even if not all matches are played
- **Points System** - 3 points for win, 1 point for draw, 0 points for loss
- **Match Scheduling** - Home player selects track (dropdown or manual entry)
- **History Tracking** - View history per player, tournament, league round, and overall league
- **Player Statistics** - Wins, Draws, Losses, Goals For/Against, Series Won, Favorite Opponent, Revenge Opportunities
- **Dark Mode** - Default dark mode with light mode toggle available
- **Mock Login** - Simple login for testing purposes (admin@example.com / admin123)
- **Unit Tests** - Comprehensive test suite with pytest

### Upcoming Features (Phase 2+)

- User registration with email verification
- Tournament system (single/double elimination)
- Support for additional competitive games

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
4. Initialize the database:
   ```bash
   flask init-db
   ```
5. (Optional) Seed test data:
   ```bash
   flask seed-data
   ```
6. Run the development server:
   ```bash
   flask run
   ```

## Testing

Run the test suite with pytest:
```bash
pytest
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
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript

## License

[License information]
