from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    failed_login_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=False)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_dummy = db.Column(db.Boolean, default=False)

class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    unique_id = db.Column(db.String(20), unique=True, nullable=True)
    game = db.relationship('Game', backref='leagues')
    owner = db.relationship('User', backref='owned_leagues')

class LeagueRound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))
    round_number = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)
    league = db.relationship('League', backref='rounds')

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))
    round_id = db.Column(db.Integer, db.ForeignKey('league_round.id'))
    home_player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    away_player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    home_track = db.Column(db.String(100), nullable=True)
    away_track = db.Column(db.String(100), nullable=True)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    is_draw = db.Column(db.Boolean, default=False)
    is_walkover = db.Column(db.Boolean, default=False)
    played_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, played, walkover, cancelled
    walkover_winner = db.Column(db.Integer, nullable=True)  # 1 for home, 2 for away
    league = db.relationship('League', backref='matches')
    round = db.relationship('LeagueRound', backref='matches')
    home_player = db.relationship('Player', foreign_keys=[home_player_id])
    away_player = db.relationship('Player', foreign_keys=[away_player_id])
