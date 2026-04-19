import click
from flask import Flask
from flask.cli import with_appcontext
from app.models.models import db, Player, Game, User
from werkzeug.security import generate_password_hash
from datetime import datetime

DUMMY_PLAYERS = [
    'Mario', 'Luigi', 'Peach', 'Daisy',
    'Toad', 'Yoshi', 'Shy Guy', 'Donkey Kong',
    'Wario', 'Waluigi', 'Bowser', 'Bowser Jr.'
]

DEFAULT_GAMES = [
    {'name': 'Mario Kart 8 Deluxe', 'platform': 'Nintendo Switch', 'max_players': 12, 'allow_tournament': True, 'allow_league': True},
    {'name': 'Mario Kart 8', 'platform': 'Nintendo Switch', 'max_players': 12, 'allow_tournament': True, 'allow_league': True},
    {'name': 'Mario Kart World', 'platform': 'Nintendo Switch 2', 'max_players': 24, 'allow_tournament': True, 'allow_league': True}
]

@click.command('init-db')
@with_appcontext
def init_db():
    db.create_all()
    
    for player_name in DUMMY_PLAYERS:
        existing = Player.query.filter_by(name=player_name).first()
        if not existing:
            player = Player(name=player_name, is_dummy=True)
            db.session.add(player)
    
    for game_data in DEFAULT_GAMES:
        existing = Game.query.filter_by(name=game_data['name']).first()
        if not existing:
            game = Game(**game_data)
            db.session.add(game)
    
    db.session.commit()
    click.echo('Database initialized with dummy players and games.')

@click.command('create-admin')
@with_appcontext
def create_admin():
    """Create or reset the admin user."""
    admin = User.query.filter_by(email='even.teigland@gmail.com').first()
    
    if not admin:
        admin = User(
            username='Teiteland',
            email='even.teigland@gmail.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        click.echo('Admin user created: Teiteland (even.teigland@gmail.com)')
    else:
        admin.username = 'Teiteland'
        admin.password_hash = generate_password_hash('admin123')
        admin.is_admin = True
        admin.is_locked = False
        admin.failed_login_attempts = 0
        click.echo('Admin user reset: Teiteland (even.teigland@gmail.com)')
    
    db.session.commit()
    click.echo('Password: admin123')

@click.command('seed-data')
@with_appcontext
def seed_data():
    from app.models.models import League, LeagueRound, Match
    players = Player.query.all()
    game = Game.query.first()
    test_user = User.query.filter_by(email='bruker@example.com').first()
    
    if not game:
        click.echo('No game found. Run init-db first.')
        return
    
    league = League(name='Test League - Season 1', game_id=game.id, owner_id=test_user.id if test_user else None)
    db.session.add(league)
    db.session.flush()
    
    player_ids = [p.id for p in players[:4]]
    
    # Round 1: Mario vs Luigi (both home & away), Peach vs Daisy (both home & away)
    round1 = LeagueRound(league_id=league.id, round_number=1, is_active=True)
    db.session.add(round1)
    db.session.flush()
    
    # Mario (home) vs Luigi - PLAYED
    match1 = Match(league_id=league.id, round_id=round1.id,
          home_player_id=player_ids[0], away_player_id=player_ids[1],
          home_score=3, away_score=1, is_draw=False,
          played_at=datetime(2024, 1, 1), home_track='Rainbow Road',
          status='played')
    db.session.add(match1)
    
    # Luigi (home) vs Mario - PLAYED
    match2 = Match(league_id=league.id, round_id=round1.id,
          home_player_id=player_ids[1], away_player_id=player_ids[0],
          home_score=0, away_score=2, is_draw=False,
          played_at=datetime(2024, 1, 1), home_track='Toad Harbor',
          status='played')
    db.session.add(match2)
    
    # Peach (home) vs Daisy - NOT PLAYED (will show as Next Match)
    match3 = Match(league_id=league.id, round_id=round1.id,
          home_player_id=player_ids[2], away_player_id=player_ids[3],
          home_track='Mario Circuit')
    db.session.add(match3)
    
    # Daisy (home) vs Peach - NOT PLAYED (will show as Next Match)
    match4 = Match(league_id=league.id, round_id=round1.id,
          home_player_id=player_ids[3], away_player_id=player_ids[2],
          home_track='Mountin')
    db.session.add(match4)
    
    # Round 2: Mario vs Peach, Luigi vs Daisy + reverses (locked initially)
    round2 = LeagueRound(league_id=league.id, round_number=2, is_active=False)
    db.session.add(round2)
    db.session.flush()
    
    # Mario (home) vs Peach
    match5 = Match(league_id=league.id, round_id=round2.id,
          home_player_id=player_ids[0], away_player_id=player_ids[2],
          home_score=4, away_score=0, is_draw=False,
          played_at=datetime(2024, 1, 8), home_track='Electrodrome',
          status='played')
    db.session.add(match5)
    
    # Peach (home) vs Mario
    match6 = Match(league_id=league.id, round_id=round2.id,
          home_player_id=player_ids[2], away_player_id=player_ids[0],
          home_score=1, away_score=2, is_draw=False,
          played_at=datetime(2024, 1, 8), home_track='SherbetLand',
          status='played')
    db.session.add(match6)
    
    # Luigi (home) vs Daisy
    match7 = Match(league_id=league.id, round_id=round2.id,
          home_player_id=player_ids[1], away_player_id=player_ids[3],
          home_score=2, away_score=1, is_draw=False,
          played_at=datetime(2024, 1, 8), home_track='Toad Harbor',
          status='played')
    db.session.add(match7)
    
    # Daisy (home) vs Luigi
    match8 = Match(league_id=league.id, round_id=round2.id,
          home_player_id=player_ids[3], away_player_id=player_ids[1],
          home_score=0, away_score=3, is_draw=False,
          played_at=datetime(2024, 1, 8), home_track='Mountin',
          status='played')
    db.session.add(match8)
    
    # Round 3: Mario vs Daisy, Luigi vs Peach + reverses (locked initially)
    round3 = LeagueRound(league_id=league.id, round_number=3, is_active=False)
    db.session.add(round3)
    db.session.flush()
    
    # Mario (home) vs Daisy
    match9 = Match(league_id=league.id, round_id=round3.id,
          home_player_id=player_ids[0], away_player_id=player_ids[3],
          home_score=5, away_score=2, is_draw=False,
          played_at=datetime(2024, 1, 15), home_track='Rainbow Road',
          status='played')
    db.session.add(match9)
    
    # Daisy (home) vs Mario
    match10 = Match(league_id=league.id, round_id=round3.id,
          home_player_id=player_ids[3], away_player_id=player_ids[0],
          home_score=1, away_score=4, is_draw=False,
          played_at=datetime(2024, 1, 15), home_track='Mountin',
          status='played')
    db.session.add(match10)
    
    # Luigi (home) vs Peach
    match11 = Match(league_id=league.id, round_id=round3.id,
          home_player_id=player_ids[1], away_player_id=player_ids[2],
          home_score=3, away_score=3, is_draw=True,
          played_at=datetime(2024, 1, 15), home_track='Toad Harbor',
          status='played')
    db.session.add(match11)
    
    # Peach (home) vs Luigi
    match12 = Match(league_id=league.id, round_id=round3.id,
          home_player_id=player_ids[2], away_player_id=player_ids[1],
          home_score=2, away_score=2, is_draw=True,
          played_at=datetime(2024, 1, 15), home_track='Mario Circuit',
          status='played')
    db.session.add(match12)
    
    # Season 2 (completed)
    league2 = League(name='Test League - Season 2', game_id=game.id, status='completed', owner_id=test_user.id if test_user else None)
    db.session.add(league2)
    db.session.flush()
    
    r1 = LeagueRound(league_id=league2.id, round_number=1)
    db.session.add(r1)
    db.session.flush()
    
    # Same structure as Season 1, different results
    db.session.add(Match(
        league_id=league2.id, round_id=r1.id,
        home_player_id=player_ids[0], away_player_id=player_ids[1],
        home_score=5, away_score=2, is_draw=False,
        played_at=datetime(2024, 2, 1), home_track='Rainbow Road'))
    db.session.add(Match(
        league_id=league2.id, round_id=r1.id,
        home_player_id=player_ids[1], away_player_id=player_ids[0],
        home_score=1, away_score=4, is_draw=False,
        played_at=datetime(2024, 2, 1), home_track='Toad Harbor'))
    db.session.add(Match(
        league_id=league2.id, round_id=r1.id,
        home_player_id=player_ids[2], away_player_id=player_ids[3],
        home_score=0, away_score=3, is_draw=False,
        played_at=datetime(2024, 2, 1), home_track='Mario Circuit'))
    db.session.add(Match(
        league_id=league2.id, round_id=r1.id,
        home_player_id=player_ids[3], away_player_id=player_ids[2],
        home_score=2, away_score=1, is_draw=False,
        played_at=datetime(2024, 2, 1), home_track='Mountin'))
    
    r2 = LeagueRound(league_id=league2.id, round_number=2)
    db.session.add(r2)
    db.session.flush()
    
    db.session.add(Match(
        league_id=league2.id, round_id=r2.id,
        home_player_id=player_ids[0], away_player_id=player_ids[2],
        home_score=3, away_score=1, is_draw=False,
        played_at=datetime(2024, 2, 8), home_track='Electrodrome'))
    db.session.add(Match(
        league_id=league2.id, round_id=r2.id,
        home_player_id=player_ids[2], away_player_id=player_ids[0],
        home_score=0, away_score=2, is_draw=False,
        played_at=datetime(2024, 2, 8), home_track='SherbetLand'))
    db.session.add(Match(
        league_id=league2.id, round_id=r2.id,
        home_player_id=player_ids[1], away_player_id=player_ids[3],
        home_score=4, away_score=0, is_draw=False,
        played_at=datetime(2024, 2, 8), home_track='Toad Harbor'))
    db.session.add(Match(
        league_id=league2.id, round_id=r2.id,
        home_player_id=player_ids[3], away_player_id=player_ids[1],
        home_score=1, away_score=5, is_draw=False,
        played_at=datetime(2024, 2, 8), home_track='Mountin'))
    
    db.session.commit()
    click.echo('Seed data created with round-robin structure (home + away in same round).')

@click.command('migrate-users')
@with_appcontext
def migrate_users():
    """Migrate existing Users to Players (for users created before auto-creation was added)."""
    users = User.query.all()
    migrated = 0
    
    for user in users:
        existing = Player.query.filter_by(name=user.username).first()
        if not existing:
            player = Player(name=user.username, is_dummy=False)
            db.session.add(player)
            migrated += 1
    
    db.session.commit()
    click.echo(f'Migrated {migrated} users to players.')
