import pytest
from app import create_app
from app.models.models import db, Player, Game, League, LeagueRound, Match, User
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

def create_test_data(app):
    with app.app_context():
        game = Game(name='Mario Kart 8 Deluxe', platform='Nintendo Switch')
        db.session.add(game)
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
        
        league = League(name='Test Season 1', game_id=game.id)
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
            'league': league
        }

def test_mario_stats(app, client):
    create_test_data(app)
    with app.app_context():
        player = Player.query.filter_by(name='Mario').first()
        response = client.get(f'/players/{player.id}')
        
        assert response.status_code == 200
        html = response.data.decode()
        
        assert 'Wins' in html
        assert '3' in html
        assert 'Draws' in html
        assert '0' in html
        assert 'Losses' in html
        assert '1' in html

def test_luigi_stats(app, client):
    create_test_data(app)
    with app.app_context():
        player = Player.query.filter_by(name='Luigi').first()
        response = client.get(f'/players/{player.id}')
        
        assert response.status_code == 200
        html = response.data.decode()
        
        assert 'Wins' in html
        assert '1' in html

def test_peach_stats(app, client):
    create_test_data(app)
    with app.app_context():
        player = Player.query.filter_by(name='Peach').first()
        response = client.get(f'/players/{player.id}')
        
        assert response.status_code == 200
        html = response.data.decode()
        
        assert 'Wins' in html
        assert '2' in html
        assert 'Draws' in html
        assert '1' in html

def test_bowser_stats(app, client):
    create_test_data(app)
    with app.app_context():
        player = Player.query.filter_by(name='Bowser').first()
        response = client.get(f'/players/{player.id}')
        
        assert response.status_code == 200
        html = response.data.decode()
        
        assert 'Losses' in html
        assert '2' in html

def test_favorite_opponent(app, client):
    with app.app_context():
        create_test_data(app)
        
        player = Player.query.filter_by(name='Mario').first()
        player_id = player.id
        print(f"Mario player_id: {player_id}")
        
        # Verify Mario has matches from create_test_data
        initial_matches = Match.query.filter(
            (Match.home_player_id == player_id) | (Match.away_player_id == player_id)
        ).all()
        print(f"Initial matches for Mario: {len(initial_matches)}")
        
        player4 = Player.query.filter_by(name='Bowser').first()
        
        league = League.query.first()
        r = LeagueRound(league_id=league.id, round_number=99)
        db.session.add(r)
        db.session.flush()
        
        new_match = Match(league_id=league.id, round_id=r.id,
              home_player_id=player_id, away_player_id=player4.id,
              home_score=5, away_score=0, is_draw=False,
              played_at=datetime(2024, 2, 1), home_track='Test')
        db.session.add(new_match)
        
        new_match2 = Match(league_id=league.id, round_id=r.id,
              home_player_id=player_id, away_player_id=player4.id,
              home_score=6, away_score=1, is_draw=False,
              played_at=datetime(2024, 2, 8), home_track='Test2')
        db.session.add(new_match2)
        
        db.session.commit()
        
        # Verify new matches were added
        all_matches = Match.query.filter(
            (Match.home_player_id == player_id) | (Match.away_player_id == player_id)
        ).all()
        print(f"All matches for Mario after adding: {len(all_matches)}")
        
        response = client.get(f'/players/{player_id}')
        
        assert response.status_code == 200
        html = response.data.decode()
        
        assert 'Favorite Opponent' in html, f"HTML: {html[:500]}"
        assert 'Bowser' in html

def test_revenge_opportunities(app, client):
    with app.app_context():
        create_test_data(app)
        
        player = Player.query.filter_by(name='Peach').first()
        player_id = player.id
        print(f"Peach player_id: {player_id}")
        
        player2 = Player.query.filter_by(name='Mario').first()
        
        league = League.query.first()
        r = LeagueRound(league_id=league.id, round_number=99)
        db.session.add(r)
        db.session.flush()
        
        new_match = Match(league_id=league.id, round_id=r.id,
              home_player_id=player2.id, away_player_id=player_id,
              home_score=3, away_score=1, is_draw=False,
              played_at=datetime(2024, 2, 1), home_track='Test')
        db.session.add(new_match)
        
        db.session.commit()
        
        all_matches = Match.query.filter(
            (Match.home_player_id == player_id) | (Match.away_player_id == player_id)
        ).all()
        print(f"All matches for Peach: {len(all_matches)}")
        for m in all_matches:
            print(f"  Match: home={m.home_player_id}, away={m.away_player_id}, home_score={m.home_score}, away_score={m.away_score}, played={m.played_at}")
        
        response = client.get(f'/players/{player_id}')
        
        assert response.status_code == 200
        html = response.data.decode()
        
        assert 'Revenge Opportunities' in html, f"HTML: {html[:500]}"
        assert 'Mario' in html

def test_series_won(app, client):
    create_test_data(app)
    with app.app_context():
        player = Player.query.filter_by(name='Mario').first()
        
        league = League.query.first()
        league.status = 'completed'
        db.session.commit()
        
        response = client.get(f'/players/{player.id}')
        
        assert response.status_code == 200
        html = response.data.decode()
        
        assert 'Series Won' in html
        assert '1' in html

def test_index_page(app, client):
    create_test_data(app)
    response = client.get('/')
    assert response.status_code == 200

def test_leagues_page(app, client):
    create_test_data(app)
    response = client.get('/leagues')
    assert response.status_code == 200

def test_league_page(app, client):
    create_test_data(app)
    with app.app_context():
        league = League.query.first()
        response = client.get(f'/leagues/{league.id}')
        assert response.status_code == 200

def test_players_page(app, client):
    create_test_data(app)
    response = client.get('/players')
    assert response.status_code == 200