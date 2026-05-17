import pytest
from app import create_app
from app.models.models import db, Player, League, LeagueRound, Match, User
from werkzeug.security import generate_password_hash
from datetime import datetime

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, username='testuser'):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = username
        sess['is_admin'] = False

def create_test_data(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com', password_hash='hash')
        db.session.add(user)
        db.session.flush()
        
        players = [
            Player(name='Mario', is_dummy=True),
            Player(name='Luigi', is_dummy=True),
            Player(name='Peach', is_dummy=True),
            Player(name='Bowser', is_dummy=True),
        ]
        for p in players:
            db.session.add(p)
        
        db.session.flush()
        
        league = League(name='Test Season 1', game_name='Mario Kart 8 Deluxe')
        db.session.add(league)
        db.session.flush()
        
        round1 = LeagueRound(league_id=league.id, round_number=1)
        db.session.add(round1)
        db.session.flush()
        
        Match(league_id=league.id, round_id=round1.id,
              home_player_id=players[0].id, away_player_id=players[1].id,
              home_score=3, away_score=1, is_draw=False,
              played_at=datetime(2024, 1, 1), home_track='Rainbow Road')
        Match(league_id=league.id, round_id=round1.id,
              home_player_id=players[2].id, away_player_id=players[3].id,
              home_score=2, away_score=2, is_draw=True,
              played_at=datetime(2024, 1, 1), home_track='Mario Circuit')
        
        round2 = LeagueRound(league_id=league.id, round_number=2)
        db.session.add(round2)
        db.session.flush()
        
        Match(league_id=league.id, round_id=round2.id,
              home_player_id=players[1].id, away_player_id=players[0].id,
              home_score=0, away_score=2, is_draw=False,
              played_at=datetime(2024, 1, 8), home_track='Toad Harbor')
        Match(league_id=league.id, round_id=round2.id,
              home_player_id=players[3].id, away_player_id=players[2].id,
              home_score=1, away_score=3, is_draw=False,
              played_at=datetime(2024, 1, 8), home_track='Mountain')
        
        round3 = LeagueRound(league_id=league.id, round_number=3)
        db.session.add(round3)
        db.session.flush()
        
        Match(league_id=league.id, round_id=round3.id,
              home_player_id=players[0].id, away_player_id=players[2].id,
              home_score=4, away_score=0, is_draw=False,
              played_at=datetime(2024, 1, 15), home_track='Electrodrome')
        Match(league_id=league.id, round_id=round3.id,
              home_player_id=players[1].id, away_player_id=players[3].id,
              home_score=2, away_score=1, is_draw=False,
              played_at=datetime(2024, 1, 15), home_track='SherbetLand')
        
        db.session.commit()
        
        return {
            'players': players,
            'league': league,
            'user': user
        }

def test_index_page_redirects_when_logged_out(app, client):
    create_test_data(app)
    response = client.get('/')
    assert response.status_code == 302

def test_leagues_page(app, client):
    create_test_data(app)
    login(client)
    response = client.get('/leagues')
    assert response.status_code == 200

def test_league_page(app, client):
    create_test_data(app)
    login(client)
    with app.app_context():
        league = League.query.first()
        response = client.get(f'/leagues/{league.id}')
        assert response.status_code == 200

def test_players_page(app, client):
    create_test_data(app)
    login(client)
    response = client.get('/players')
    assert response.status_code == 200

def test_players_require_login(app, client):
    create_test_data(app)
    response = client.get('/players')
    assert response.status_code == 302

def test_player_stats_require_login(app, client):
    create_test_data(app)
    with app.app_context():
        player = Player.query.filter_by(name='Mario').first()
        response = client.get(f'/players/{player.id}')
        assert response.status_code == 302
