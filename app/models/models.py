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
    platform = db.Column(db.String(50), nullable=True)
    max_players = db.Column(db.Integer, nullable=True)
    allow_tournament = db.Column(db.Boolean, default=True)
    allow_league = db.Column(db.Boolean, default=True)
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

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    unique_id = db.Column(db.String(20), unique=True, nullable=True)
    format = db.Column(db.String(20), default='single_elimination')  # single_elimination, double_elimination
    best_of = db.Column(db.Integer, default=1)  # 1 for single game, 3 for best of 3 in grand finals
    status = db.Column(db.String(20), default='draft')  # draft, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    game = db.relationship('Game', backref='tournaments')
    owner = db.relationship('User', backref='owned_tournaments')

class TournamentPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    seed_number = db.Column(db.Integer, nullable=True)
    eliminated = db.Column(db.Boolean, default=False)
    placement = db.Column(db.Integer, nullable=True)
    tournament = db.relationship('Tournament', backref='tournament_players')
    player = db.relationship('Player', backref='tournament_participations')

class TournamentMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    bracket = db.Column(db.String(20), default='winners')  # winners, losers, grand_finals
    round_number = db.Column(db.Integer, nullable=False)  # Round in bracket (1 = first round)
    match_number = db.Column(db.Integer, nullable=False)  # Match within the round
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    score1 = db.Column(db.Integer, nullable=True)
    score2 = db.Column(db.Integer, nullable=True)
    is_bye = db.Column(db.Boolean, default=False)
    next_match_id = db.Column(db.Integer, db.ForeignKey('tournament_match.id'), nullable=True)
    loser_next_match_id = db.Column(db.Integer, db.ForeignKey('tournament_match.id'), nullable=True)
    played_at = db.Column(db.DateTime, nullable=True)
    tournament = db.relationship('Tournament', backref='matches')
    player1 = db.relationship('Player', foreign_keys=[player1_id])
    player2 = db.relationship('Player', foreign_keys=[player2_id])
    winner = db.relationship('Player', foreign_keys=[winner_id])
    next_match = db.relationship('TournamentMatch', foreign_keys=[next_match_id], remote_side=[id])
    loser_next_match = db.relationship('TournamentMatch', foreign_keys=[loser_next_match_id], remote_side=[id])
