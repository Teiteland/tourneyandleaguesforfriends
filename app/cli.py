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
    {'name': 'Mario Kart 8 Deluxe', 'platform': 'Nintendo Switch'},
    {'name': 'Mario Kart 8', 'platform': 'Nintendo Switch'},
    {'name': 'Mario Kart World', 'platform': 'Nintendo Switch 2'}
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
    
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            username='Admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
    
    db.session.commit()
    click.echo('Database initialized with dummy players, games, and admin user.')

@click.command('seed-data')
@with_appcontext
def seed_data():
    from app.models.models import League, LeagueRound, Match
    players = Player.query.all()
    game = Game.query.first()
    
    if not game:
        click.echo('No game found. Run init-db first.')
        return
    
    league = League(name='Test League - Season 1', game_id=game.id)
    db.session.add(league)
    db.session.flush()
    
    player_ids = [p.id for p in players[:4]]
    
    round1 = LeagueRound(league_id=league.id, round_number=1)
    db.session.add(round1)
    db.session.flush()
    
    Match(league_id=league.id, round_id=round1.id,
          home_player_id=player_ids[0], away_player_id=player_ids[1],
          home_score=3, away_score=1, is_draw=False,
          played_at=datetime(2024, 1, 1), home_track='Rainbow Road')
    Match(league_id=league.id, round_id=round1.id,
          home_player_id=player_ids[2], away_player_id=player_ids[3],
          home_score=2, away_score=2, is_draw=True,
          played_at=datetime(2024, 1, 1), home_track='Mario Circuit')
    
    round2 = LeagueRound(league_id=league.id, round_number=2)
    db.session.add(round2)
    db.session.flush()
    
    Match(league_id=league.id, round_id=round2.id,
          home_player_id=player_ids[1], away_player_id=player_ids[0],
          home_score=0, away_score=2, is_draw=False,
          played_at=datetime(2024, 1, 8), home_track='Toad Harbor')
    Match(league_id=league.id, round_id=round2.id,
          home_player_id=player_ids[3], away_player_id=player_ids[2],
          home_score=1, away_score=3, is_draw=False,
          played_at=datetime(2024, 1, 8), home_track='Mountain')
    
    round3 = LeagueRound(league_id=league.id, round_number=3)
    db.session.add(round3)
    db.session.flush()
    
    Match(league_id=league.id, round_id=round3.id,
          home_player_id=player_ids[0], away_player_id=player_ids[2],
          home_score=4, away_score=0, is_draw=False,
          played_at=datetime(2024, 1, 15), home_track='Electrodrome')
    Match(league_id=league.id, round_id=round3.id,
          home_player_id=player_ids[1], away_player_id=player_ids[3],
          home_score=2, away_score=1, is_draw=False,
          played_at=datetime(2024, 1, 15), home_track='SherbetLand')
    
    league2 = League(name='Test League - Season 2', game_id=game.id, status='completed')
    db.session.add(league2)
    db.session.flush()
    
    r1 = LeagueRound(league_id=league2.id, round_number=1)
    db.session.add(r1)
    db.session.flush()
    
    Match(league_id=league2.id, round_id=r1.id,
          home_player_id=player_ids[0], away_player_id=player_ids[1],
          home_score=5, away_score=2, is_draw=False,
          played_at=datetime(2024, 2, 1), home_track='Rainbow Road')
    Match(league_id=league2.id, round_id=r1.id,
          home_player_id=player_ids[2], away_player_id=player_ids[3],
          home_score=1, away_score=4, is_draw=False,
          played_at=datetime(2024, 2, 1), home_track='Mario Circuit')
    
    r2 = LeagueRound(league_id=league2.id, round_number=2)
    db.session.add(r2)
    db.session.flush()
    
    Match(league_id=league2.id, round_id=r2.id,
          home_player_id=player_ids[1], away_player_id=player_ids[2],
          home_score=0, away_score=3, is_draw=False,
          played_at=datetime(2024, 2, 8), home_track='Toad Harbor')
    Match(league_id=league2.id, round_id=r2.id,
          home_player_id=player_ids[3], away_player_id=player_ids[0],
          home_score=2, away_score=1, is_draw=False,
          played_at=datetime(2024, 2, 8), home_track='Mountain')
    
    db.session.commit()
    click.echo('Seed data created with more comprehensive test matches.')
