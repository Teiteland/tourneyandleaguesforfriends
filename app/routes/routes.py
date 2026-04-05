from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.models import db, League, LeagueRound, Match, Player, Game, User
from werkzeug.security import check_password_hash
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    leagues = League.query.order_by(League.created_at.desc()).all()
    default_theme = 'dark'
    return render_template('index.html', leagues=leagues, default_theme=default_theme)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.index'))

@main.route('/leagues')
def leagues():
    all_leagues = League.query.order_by(League.created_at.desc()).all()
    return render_template('leagues.html', leagues=all_leagues)

@main.route('/leagues/create', methods=['GET', 'POST'])
def create_league():
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('main.leagues'))
    
    games = Game.query.all()
    players = Player.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        game_id = request.form.get('game_id')
        selected_players = request.form.getlist('players')
        
        if not name or not game_id:
            flash('Name and game are required', 'error')
            return render_template('create_league.html', games=games, players=players)
        
        league = League(name=name, game_id=game_id)
        db.session.add(league)
        db.session.flush()
        
        generate_round_robin(league, selected_players)
        
        db.session.commit()
        flash(f'League "{name}" created successfully!', 'success')
        return redirect(url_for('main.league', league_id=league.id))
    
    return render_template('create_league.html', games=games, players=players)

@main.route('/leagues/<int:league_id>')
def league(league_id):
    league = League.query.get_or_404(league_id)
    rounds = LeagueRound.query.filter_by(league_id=league_id).order_by(LeagueRound.round_number).all()
    
    matches_by_round = {}
    for round_obj in rounds:
        matches = Match.query.filter_by(round_id=round_obj.id).all()
        matches_by_round[round_obj.round_number] = matches
    
    standings = calculate_standings(league_id)
    
    return render_template('league.html', league=league, rounds=rounds, 
                           matches_by_round=matches_by_round, standings=standings)

@main.route('/leagues/<int:league_id>/end')
def end_league(league_id):
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    league = League.query.get_or_404(league_id)
    league.status = 'completed'
    league.ended_at = datetime.utcnow()
    db.session.commit()
    flash(f'League "{league.name}" has been ended', 'success')
    return redirect(url_for('main.league', league_id=league_id))

@main.route('/leagues/<int:league_id>/match/<int:match_id>', methods=['GET', 'POST'])
def match(league_id, match_id):
    league = League.query.get_or_404(league_id)
    match = Match.query.get_or_404(match_id)
    
    if request.method == 'POST':
        home_score = request.form.get('home_score')
        away_score = request.form.get('away_score')
        
        if home_score is not None and away_score is not None:
            match.home_score = int(home_score)
            match.away_score = int(away_score)
            match.is_draw = match.home_score == match.away_score
            match.played_at = datetime.utcnow()
            db.session.commit()
            flash('Match result saved!', 'success')
    
    return render_template('match.html', league=league, match=match)

@main.route('/players')
def players():
    all_players = Player.query.all()
    return render_template('players.html', players=all_players)

@main.route('/players/<int:player_id>')
def player(player_id):
    player = Player.query.get_or_404(player_id)
    matches = Match.query.filter(
        ((Match.home_player_id == player_id) | (Match.away_player_id == player_id)) &
        (Match.home_score.isnot(None))
    ).order_by(Match.played_at.desc()).all()
    
    wins = 0
    draws = 0
    losses = 0
    goals_for = 0
    goals_against = 0
    
    opponent_wins = {}
    loss_history = []
    
    for m in matches:
        if player_id == m.home_player_id:
            goals_for += m.home_score
            goals_against += m.away_score
            opponent_id = m.away_player_id
            if m.home_score > m.away_score:
                wins += 1
                opponent_wins[opponent_id] = opponent_wins.get(opponent_id, 0) + 1
            elif m.home_score < m.away_score:
                losses += 1
                if m.played_at:
                    loss_history.append({
                        'opponent_id': opponent_id,
                        'opponent_name': m.away_player.name if m.away_player else 'Unknown',
                        'date': m.played_at,
                        'score': f'{m.home_score}-{m.away_score}'
                    })
            else:
                draws += 1
        else:
            goals_for += m.away_score
            goals_against += m.home_score
            opponent_id = m.home_player_id
            if m.away_score > m.home_score:
                wins += 1
                opponent_wins[opponent_id] = opponent_wins.get(opponent_id, 0) + 1
            elif m.away_score < m.home_score:
                losses += 1
                if m.played_at:
                    loss_history.append({
                        'opponent_id': opponent_id,
                        'opponent_name': m.home_player.name if m.home_player else 'Unknown',
                        'date': m.played_at,
                        'score': f'{m.home_score}-{m.away_score}'
                    })
            else:
                draws += 1
    
    max_wins = max(opponent_wins.values()) if opponent_wins else 0
    if max_wins > 0:
        favorites = [pid for pid, w in opponent_wins.items() if w == max_wins]
        import random
        fav_id = random.choice(favorites)
        fav_player = Player.query.get(fav_id)
        favorite_opponent = {
            'name': fav_player.name if fav_player else 'Unknown',
            'wins': max_wins
        }
    else:
        favorite_opponent = None
    
    revenge_opportunities = []
    for loss in loss_history[:20]:
        has_revenge = False
        for m in matches:
            if m.played_at and loss['date']:
                if loss['opponent_id'] == m.home_player_id and player_id == m.away_player_id:
                    if m.away_score > m.home_score and m.played_at > loss['date']:
                        has_revenge = True
                        break
                elif loss['opponent_id'] == m.away_player_id and player_id == m.home_player_id:
                    if m.home_score > m.away_score and m.played_at > loss['date']:
                        has_revenge = True
                        break
        if not has_revenge:
            revenge_opportunities.append(loss)
        if len(revenge_opportunities) >= 5:
            break
    
    from app.models.models import League
    leagues = League.query.all()
    series_won = 0
    for league in leagues:
        from app.routes.routes import calculate_standings
        standings = calculate_standings(league.id)
        for s in standings:
            if s['player_id'] == player_id and s['position'] == 1:
                series_won += 1
                break
    
    return render_template('player.html', player=player, matches=matches,
                          wins=wins, draws=draws, losses=losses,
                          goals_for=goals_for, goals_against=goals_against,
                          series_won=series_won,
                          favorite_opponent=favorite_opponent,
                          revenge_opportunities=revenge_opportunities)

def generate_round_robin(league, player_ids):
    if len(player_ids) < 2:
        return
    
    players = list(player_ids)
    n = len(players)
    has_bye = n % 2 == 1
    
    if has_bye:
        players.append(None)
        n += 1
    
    num_rounds = n - 1
    
    for round_num in range(num_rounds):
        league_round = LeagueRound(league_id=league.id, round_number=round_num + 1)
        db.session.add(league_round)
        db.session.flush()
        
        used = set()
        
        for i in range(n // 2):
            home = players[i]
            away = players[n - 1 - i]
            
            if home is not None and away is not None:
                match = Match(league_id=league.id, round_id=league_round.id,
                              home_player_id=home, away_player_id=away, home_track='Home')
                db.session.add(match)
                used.add(home)
                used.add(away)
                
                match2 = Match(league_id=league.id, round_id=league_round.id,
                              home_player_id=away, away_player_id=home, home_track='Away')
                db.session.add(match2)
                used.add(home)
                used.add(away)
        
        if has_bye:
            for p in player_ids:
                if p not in used:
                    m1 = Match(league_id=league.id, round_id=league_round.id,
                               home_player_id=p, away_player_id=None,
                               home_score=0, away_score=0, is_walkover=True,
                               played_at=datetime.utcnow(), home_track='WO')
                    db.session.add(m1)
                    m2 = Match(league_id=league.id, round_id=league_round.id,
                               home_player_id=None, away_player_id=p,
                               home_score=0, away_score=0, is_walkover=True,
                               played_at=datetime.utcnow(), home_track='WO')
                    db.session.add(m2)
                    break
        
        players = [players[0]] + [players[-1]] + players[1:-1]

def calculate_standings(league_id):
    league = League.query.get_or_404(league_id)
    matches = Match.query.filter_by(league_id=league_id).all()
    
    standings = {}
    
    for match in matches:
        if match.home_player_id is not None and match.home_player_id not in standings:
            player = Player.query.get(match.home_player_id)
            standings[match.home_player_id] = {
                'player_id': match.home_player_id,
                'name': player.name,
                'played': 0,
                'won': 0,
                'drawn': 0,
                'lost': 0,
                'points': 0
            }
        
        if match.away_player_id is not None and match.away_player_id not in standings:
            player = Player.query.get(match.away_player_id)
            standings[match.away_player_id] = {
                'player_id': match.away_player_id,
                'name': player.name,
                'played': 0,
                'won': 0,
                'drawn': 0,
                'lost': 0,
                'points': 0
            }
        
        if match.home_score is not None:
            if not match.is_walkover:
                if match.home_player_id is not None:
                    standings[match.home_player_id]['played'] += 1
                if match.away_player_id is not None:
                    standings[match.away_player_id]['played'] += 1
                
                if match.is_draw:
                    if match.home_player_id is not None:
                        standings[match.home_player_id]['drawn'] += 1
                        standings[match.home_player_id]['points'] += 1
                    if match.away_player_id is not None:
                        standings[match.away_player_id]['drawn'] += 1
                        standings[match.away_player_id]['points'] += 1
                elif match.home_score > match.away_score:
                    if match.home_player_id is not None:
                        standings[match.home_player_id]['won'] += 1
                        standings[match.home_player_id]['points'] += 3
                    if match.away_player_id is not None:
                        standings[match.away_player_id]['lost'] += 1
                else:
                    if match.away_player_id is not None:
                        standings[match.away_player_id]['won'] += 1
                        standings[match.away_player_id]['points'] += 3
                    if match.home_player_id is not None:
                        standings[match.home_player_id]['lost'] += 1
    
    sorted_standings = sorted(standings.values(), key=lambda x: (-x['points'], -x['won'], -x['drawn']))
    
    for i, s in enumerate(sorted_standings):
        s['position'] = i + 1
    
    return sorted_standings
