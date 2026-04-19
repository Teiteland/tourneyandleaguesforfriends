from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.models import db, League, LeagueRound, Match, Player, Game, User, Tournament, TournamentMatch, TournamentPlayer, FFAMatch, FFAPlayer, LeagueJoinRequest, TournamentJoinRequest
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import math

main = Blueprint('main', __name__)

def can_manage_league(league_id):
    """Check if current user can manage the league (admin or owner)."""
    if session.get('is_admin'):
        return True
    league = League.query.get(league_id)
    return league and league.owner_id == session.get('user_id')

def can_manage_tournament(tournament_id):
    """Check if current user can manage the tournament (admin or owner)."""
    if session.get('is_admin'):
        return True
    tournament = Tournament.query.get(tournament_id)
    return tournament and tournament.owner_id == session.get('user_id')

def can_manage_ffa(ffa_id):
    """Check if current user can manage the FFA match (admin or league owner)."""
    if session.get('is_admin'):
        return True
    ffa = FFAMatch.query.get(ffa_id)
    if not ffa:
        return False
    if ffa.league_id:
        league = League.query.get(ffa.league_id)
        return league and league.owner_id == session.get('user_id')
    # For standalone FFA, check if user is owner
    return ffa and ffa.owner_id == session.get('user_id')

def can_view_league(league_id):
    """Check if current user can view the league."""
    league = League.query.get(league_id)
    if not league:
        return False
    if league.status != 'archived':
        return True
    return session.get('user_id') and (session.get('is_admin') or league.owner_id == session.get('user_id'))

@main.route('/')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))
    
    leagues = League.query.order_by(League.created_at.desc()).all()
    tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
    default_theme = 'dark'
    return render_template('index.html', leagues=leagues, tournaments=tournaments, default_theme=default_theme)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()
        
        if user and user.is_locked:
            flash('Your account is locked. Please contact an admin.', 'error')
            return render_template('login.html')
        
        if user and check_password_hash(user.password_hash, password):
            user.failed_login_attempts = 0
            db.session.commit()
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.is_locked = True
                    db.session.commit()
                    flash('Too many failed attempts. Your account is now locked. Contact an admin.', 'error')
                else:
                    db.session.commit()
                    flash(f'Invalid email or password. {5 - user.failed_login_attempts} attempts remaining.', 'error')
            else:
                flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        errors = []
        
        if User.query.filter_by(email=email).first():
            errors.append('Email is already registered')
        
        if User.query.filter_by(username=username).first():
            errors.append('Username is already taken')
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        
        if not any(c.isalpha() for c in password):
            errors.append('Password must contain at least one letter')
        
        if not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one number')
        
        if password != confirm:
            errors.append('Passwords do not match')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html', username=username, email=email)
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=False,
            failed_login_attempts=0,
            is_locked=False
        )
        db.session.add(user)
        db.session.commit()
        
        player = Player(name=username, is_dummy=False)
        db.session.add(player)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.index'))

@main.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        flash('Please log in to view your profile', 'error')
        return redirect(url_for('main.login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not check_password_hash(user.password_hash, current_password):
            flash('Current password is incorrect', 'error')
            return render_template('profile.html', user=user)
        
        errors = []
        
        if len(new_password) < 8:
            errors.append('Password must be at least 8 characters')
        
        if not any(c.isalpha() for c in new_password):
            errors.append('Password must contain at least one letter')
        
        if not any(c.isdigit() for c in new_password):
            errors.append('Password must contain at least one number')
        
        if new_password != confirm_password:
            errors.append('New passwords do not match')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('profile.html', user=user)
        
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('profile.html', user=user)

@main.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('main.index'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@main.route('/debug/users')
def debug_users():
    """Debug route to see all users - for troubleshooting only"""
    users = User.query.order_by(User.id).all()
    result = []
    for u in users:
        result.append(f"ID: {u.id}, Username: {u.username}, Email: {u.email}, Admin: {u.is_admin}")
    return "<br>".join(result) if result else "No users found"

@main.route('/admin/unlock/<int:user_id>')
def admin_unlock(user_id):
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    user.is_locked = False
    user.failed_login_attempts = 0
    db.session.commit()
    flash(f'User {user.username} has been unlocked', 'success')
    return redirect(url_for('main.admin_users'))

@main.route('/admin/reset-password/<int:user_id>', methods=['POST'])
def admin_reset_password(user_id):
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    errors = []
    
    if len(new_password) < 8:
        errors.append('Password must be at least 8 characters')
    
    if not any(c.isalpha() for c in new_password):
        errors.append('Password must contain at least one letter')
    
    if not any(c.isdigit() for c in new_password):
        errors.append('Password must contain at least one number')
    
    if new_password != confirm_password:
        errors.append('Passwords do not match')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('main.admin_users'))
    
    user.password_hash = generate_password_hash(new_password)
    user.failed_login_attempts = 0
    user.is_locked = False
    db.session.commit()
    flash(f'Password for {user.username} has been reset', 'success')
    return redirect(url_for('main.admin_users'))

@main.route('/admin/games')
def admin_games():
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('main.index'))
    
    games = Game.query.order_by(Game.name).all()
    return render_template('admin_games.html', games=games)

@main.route('/admin/games/create', methods=['GET', 'POST'])
def admin_create_game():
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        platform = request.form.get('platform')
        other_platform = request.form.get('other_platform')
        max_players = request.form.get('max_players')
        allow_tournament = request.form.get('allow_tournament') == 'on'
        allow_league = request.form.get('allow_league') == 'on'
        
        if not name:
            flash('Game name is required', 'error')
            return redirect(url_for('main.admin_games'))
        
        if platform == 'other' and other_platform:
            platform = other_platform
        
        game = Game(
            name=name,
            platform=platform if platform else None,
            max_players=int(max_players) if max_players else None,
            allow_tournament=allow_tournament,
            allow_league=allow_league
        )
        db.session.add(game)
        db.session.commit()
        flash(f'Game "{name}" created successfully!', 'success')
        return redirect(url_for('main.admin_games'))
    
    return render_template('admin_create_game.html')

@main.route('/admin/games/delete/<int:game_id>', methods=['POST'])
def admin_delete_game(game_id):
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('main.index'))
    
    game = Game.query.get_or_404(game_id)
    game_name = game.name
    
    if game.leagues or game.tournaments:
        game.is_active = False
        db.session.commit()
        flash(f'Game "{game_name}" has been deactivated (in use)', 'success')
    else:
        db.session.delete(game)
        db.session.commit()
        flash(f'Game "{game_name}" has been deleted', 'success')
    
    return redirect(url_for('main.admin_games'))

@main.route('/games')
def games():
    if not session.get('user_id'):
        flash('Please log in to view games', 'error')
        return redirect(url_for('main.login'))
    
    is_admin = session.get('is_admin')
    show_all = request.args.get('show_all') == 'true'
    
    if is_admin and show_all:
        all_games = Game.query.order_by(Game.name).all()
    else:
        all_games = Game.query.filter_by(is_active=True).order_by(Game.name).all()
    
    return render_template('games.html', games=all_games, is_admin=is_admin, show_all=show_all)

@main.route('/my-events')
def my_events():
    if not session.get('user_id'):
        flash('Please log in to view your events', 'error')
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    my_leagues = League.query.filter_by(owner_id=user_id).all()
    my_tournaments = Tournament.query.filter_by(owner_id=user_id).all()
    my_ffas = FFAMatch.query.filter_by(owner_id=user_id).all()
    
    return render_template('my_events.html', 
                         leagues=my_leagues, 
                         tournaments=my_tournaments,
                         ffas=my_ffas)

@main.route('/leagues')
def leagues():
    all_leagues = League.query.order_by(League.created_at.desc()).all()
    return render_template('leagues.html', leagues=all_leagues)

@main.route('/leagues/create', methods=['GET', 'POST'])
def create_league():
    if not session.get('user_id'):
        flash('Please log in to create a league', 'error')
        return redirect(url_for('main.login'))
    
    games = Game.query.filter_by(allow_league=True, is_active=True).all()
    players = Player.query.all()
    
    pre_selected_game = request.args.get('game_id')
    
    if request.method == 'POST':
        name = request.form.get('name')
        game_id = request.form.get('game_id')
        selected_players = request.form.getlist('players')
        
        if not name or not game_id:
            flash('Name and game are required', 'error')
            return render_template('create_league.html', games=games, players=players)
        
        league = League(
            name=name,
            game_id=game_id,
            owner_id=session['user_id'],
            unique_id=uuid.uuid4().hex[:12]
        )
        db.session.add(league)
        db.session.flush()
        
        generate_round_robin(league, selected_players)
        
        db.session.commit()
        flash(f'League "{name}" created successfully!', 'success')
        return redirect(url_for('main.league', league_id=league.id))
    
    return render_template('create_league.html', games=games, players=players, pre_selected_game=pre_selected_game)

@main.route('/leagues/<int:league_id>')
def league(league_id):
    league = League.query.get_or_404(league_id)
    rounds = LeagueRound.query.filter_by(league_id=league_id).order_by(LeagueRound.round_number).all()
    
    matches_by_round = {}
    for round_obj in rounds:
        matches = Match.query.filter_by(round_id=round_obj.id).all()
        matches_by_round[round_obj.round_number] = matches
    
    standings = calculate_standings(league_id)
    can_manage = can_manage_league(league_id)
    
    own_profile = None
    if session.get('user_id'):
        player_exists = Player.query.filter_by(name=session.get('username')).first()
        if player_exists:
            own_profile = player_exists
    
    return render_template('league.html', league=league, rounds=rounds, 
                           matches_by_round=matches_by_round, standings=standings,
                           can_manage=can_manage, own_profile=own_profile)

@main.route('/leagues/<int:league_id>/round/<int:round_number>/activate')
def activate_round(league_id, round_number):
    if not can_manage_league(league_id):
        flash('You do not have permission to manage this league', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    league = League.query.get_or_404(league_id)
    
    round_obj = LeagueRound.query.filter_by(
        league_id=league_id, 
        round_number=round_number
    ).first_or_404()
    
    if round_obj.is_active:
        flash('Round is already active', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    if round_obj.is_completed:
        flash('Cannot activate a completed round', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    round_obj.is_active = True
    db.session.commit()
    flash(f'Round {round_number} is now active', 'success')
    return redirect(url_for('main.league', league_id=league_id))

@main.route('/leagues/<int:league_id>/round/<int:round_number>/complete')
def complete_round(league_id, round_number):
    if not can_manage_league(league_id):
        flash('You do not have permission to manage this league', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    league = League.query.get_or_404(league_id)
    
    round_obj = LeagueRound.query.filter_by(
        league_id=league_id, 
        round_number=round_number
    ).first_or_404()
    
    if not round_obj.is_active:
        flash('Round is not active', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    if round_obj.is_completed:
        flash('Round is already completed', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    round_obj.is_completed = True
    db.session.commit()
    
    # Auto-activate next round if ALL active rounds are completed
    _auto_activate_next_round(league_id)
    
    flash(f'Round {round_number} is now completed', 'success')
    return redirect(url_for('main.league', league_id=league_id))

def _auto_activate_next_round(league_id):
    """Auto-activate next round when all active rounds are completed."""
    # Check if there are any active but not completed rounds
    active_rounds = LeagueRound.query.filter_by(
        league_id=league_id,
        is_active=True,
        is_completed=False
    ).all()
    
    if active_rounds:
        return  # There are still active rounds, don't activate next
    
    # All active rounds are completed - find next round to activate
    last_completed = LeagueRound.query.filter_by(
        league_id=league_id,
        is_completed=True
    ).order_by(LeagueRound.round_number.desc()).first()
    
    if last_completed:
        next_round_num = last_completed.round_number + 1
        next_round = LeagueRound.query.filter_by(
            league_id=league_id,
            round_number=next_round_num
        ).first()
        
        if next_round and not next_round.is_active:
            next_round.is_active = True
            db.session.commit()

@main.route('/leagues/<int:league_id>/end')
def end_league(league_id):
    if not can_manage_league(league_id):
        flash('Admin or owner access required', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    league = League.query.get_or_404(league_id)
    league.status = 'completed'
    league.ended_at = datetime.utcnow()
    db.session.commit()
    flash(f'League "{league.name}" has been ended', 'success')
    return redirect(url_for('main.league', league_id=league_id))

@main.route('/leagues/<int:league_id>/players')
def manage_league_players(league_id):
    if not can_manage_league(league_id):
        flash('You do not have permission to manage this league', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    league = League.query.get_or_404(league_id)
    
    current_player_ids = set()
    for match in league.matches:
        if match.home_player_id:
            current_player_ids.add(match.home_player_id)
        if match.away_player_id:
            current_player_ids.add(match.away_player_id)
    
    all_players = Player.query.all()
    available_players = [p for p in all_players if p.id not in current_player_ids]
    
    current_players = Player.query.filter(Player.id.in_(current_player_ids)).all() if current_player_ids else []
    
    return render_template('manage_league_players.html',
                         league=league,
                         current_players=current_players,
                         available_players=available_players)

@main.route('/leagues/<int:league_id>/players/add', methods=['POST'])
def add_league_player(league_id):
    if not can_manage_league(league_id):
        flash('You do not have permission to manage this league', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    league = League.query.get_or_404(league_id)
    if league.status == 'completed':
        flash('Cannot add players - league is completed', 'error')
        return redirect(url_for('main.manage_league_players', league_id=league_id))
    
    player_id = request.form.get('player_id')
    if not player_id:
        return redirect(url_for('main.manage_league_players', league_id=league_id))
    
    player_id = int(player_id)
    
    for match in league.matches:
        if match.home_player_id == player_id or match.away_player_id == player_id:
            flash('Player is already in the league', 'error')
            return redirect(url_for('main.manage_league_players', league_id=league_id))
    
    current_player_ids = set()
    for match in league.matches:
        if match.home_player_id:
            current_player_ids.add(match.home_player_id)
        if match.away_player_id:
            current_player_ids.add(match.away_player_id)
    
    rounds = LeagueRound.query.filter_by(league_id=league_id).order_by(LeagueRound.round_number).all()
    if not rounds:
        flash('No rounds found in this league', 'error')
        return redirect(url_for('main.manage_league_players', league_id=league_id))
    
    remaining_rounds = [r for r in rounds if not r.is_completed]
    if not remaining_rounds:
        flash('All rounds are completed', 'error')
        return redirect(url_for('main.manage_league_players', league_id=league_id))
    
    new_matches = []
    for existing_player_id in current_player_ids:
        new_matches.append({
            'home_player_id': player_id,
            'away_player_id': existing_player_id,
            'track': 'Home'
        })
        new_matches.append({
            'home_player_id': existing_player_id,
            'away_player_id': player_id,
            'track': 'Away'
        })
    
    catch_up_round = LeagueRound.query.filter_by(league_id=league_id, round_number=len(rounds) + 1).first()
    
    rounds_with_capacity = []
    for r in remaining_rounds:
        if catch_up_round and r.id == catch_up_round.id:
            continue
        current_matches_in_round = Match.query.filter_by(round_id=r.id, league_id=league_id).count()
        rounds_with_capacity.append({
            'round': r,
            'current_count': current_matches_in_round
        })
    
    matches_placed = 0
    for match_data in new_matches:
        placed = False
        for round_info in rounds_with_capacity:
            round_obj = round_info['round']
            existing_in_round = Match.query.filter(
                Match.league_id == league_id,
                Match.round_id == round_obj.id,
                db.or_(
                    db.and_(Match.home_player_id == match_data['home_player_id'], Match.away_player_id == match_data['away_player_id']),
                    db.and_(Match.home_player_id == match_data['away_player_id'], Match.away_player_id == match_data['home_player_id'])
                )
            ).first()
            
            if existing_in_round:
                continue
            
            match = Match(
                league_id=league_id,
                round_id=round_obj.id,
                home_player_id=match_data['home_player_id'],
                away_player_id=match_data['away_player_id'],
                home_track=match_data['track']
            )
            db.session.add(match)
            matches_placed += 1
            placed = True
            break
    
    remaining_matches = len(new_matches) - matches_placed
    if remaining_matches > 0:
        if not catch_up_round:
            catch_up_round = LeagueRound(
                league_id=league_id,
                round_number=len(rounds) + 1,
                is_active=False
            )
            db.session.add(catch_up_round)
            db.session.flush()
        
        for match_data in new_matches:
            already_exists = Match.query.filter(
                Match.league_id == league_id,
                Match.round_id == catch_up_round.id,
                db.or_(
                    db.and_(Match.home_player_id == match_data['home_player_id'], Match.away_player_id == match_data['away_player_id']),
                    db.and_(Match.home_player_id == match_data['away_player_id'], Match.away_player_id == match_data['home_player_id'])
                )
            ).first()
            
            if already_exists:
                continue
            
            match = Match(
                league_id=league_id,
                round_id=catch_up_round.id,
                home_player_id=match_data['home_player_id'],
                away_player_id=match_data['away_player_id'],
                home_track=match_data['track']
            )
            db.session.add(match)
    
    db.session.commit()
    flash(f'Player added with {len(new_matches)} matches', 'success')
    
    return redirect(url_for('main.manage_league_players', league_id=league_id))

@main.route('/leagues/<int:league_id>/players/remove/<int:player_id>', methods=['POST'])
def remove_league_player(league_id, player_id):
    if not can_manage_league(league_id):
        flash('You do not have permission to manage this league', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    league = League.query.get_or_404(league_id)
    if league.status == 'completed':
        flash('Cannot remove players - league is completed', 'error')
        return redirect(url_for('main.manage_league_players', league_id=league_id))
    
    player = Player.query.get_or_404(player_id)
    
    Match.query.filter(
        Match.league_id == league_id,
        db.or_(Match.home_player_id == player_id, Match.away_player_id == player_id),
        Match.home_score.is_(None)
    ).delete()
    
    db.session.commit()
    flash(f'Player {player.name} removed from league', 'success')
    
    return redirect(url_for('main.manage_league_players', league_id=league_id))

@main.route('/leagues/<int:league_id>/request-join', methods=['POST'])
def request_join_league(league_id):
    if not session.get('user_id'):
        flash('Please log in to request to join', 'error')
        return redirect(url_for('main.login'))
    
    player_id = request.form.get('player_id')
    if not player_id:
        flash('No player selected', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    player_id = int(player_id)
    
    existing_request = LeagueJoinRequest.query.filter_by(
        league_id=league_id,
        player_id=player_id,
        status='pending'
    ).first()
    
    if existing_request:
        flash('You have already requested to join this league', 'info')
        return redirect(url_for('main.league', league_id=league_id))
    
    already_in = Match.query.filter(
        Match.league_id == league_id,
        db.or_(Match.home_player_id == player_id, Match.away_player_id == player_id)
    ).first()
    
    if already_in:
        flash('You are already in this league', 'info')
        return redirect(url_for('main.league', league_id=league_id))
    
    join_request = LeagueJoinRequest(
        league_id=league_id,
        player_id=player_id,
        status='pending'
    )
    db.session.add(join_request)
    db.session.commit()
    flash('Join request sent!', 'success')
    return redirect(url_for('main.league', league_id=league_id))

@main.route('/leagues/<int:league_id>/join-requests')
def view_league_join_requests(league_id):
    if not can_manage_league(league_id):
        flash('You do not have permission to view requests', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    league = League.query.get_or_404(league_id)
    pending_requests = LeagueJoinRequest.query.filter_by(
        league_id=league_id,
        status='pending'
    ).all()
    
    return render_template('league_join_requests.html', league=league, pending_requests=pending_requests)

@main.route('/leagues/<int:league_id>/join-requests/<int:request_id>/<action>', methods=['POST'])
def handle_league_join_request(league_id, request_id, action):
    if not can_manage_league(league_id):
        flash('You do not have permission to manage requests', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    join_request = LeagueJoinRequest.query.get_or_404(request_id)
    
    if action == 'approve':
        join_request.status = 'approved'
        league = League.query.get(league_id)
        active_round = None
        for r in league.rounds:
            if r.is_active and not r.is_completed:
                active_round = r
                break
            if r.is_completed:
                continue
        
        if active_round:
            match = Match(
                league_id=league_id,
                round_id=active_round.id,
                home_player_id=join_request.player_id,
                away_player_id=None,
                home_track='New'
            )
            db.session.add(match)
        flash('Player added to league!', 'success')
    elif action == 'deny':
        join_request.status = 'denied'
        flash('Request denied', 'success')
    
    db.session.commit()
    return redirect(url_for('main.view_league_join_requests', league_id=league_id))

@main.route('/leagues/<int:league_id>/match/<int:match_id>', methods=['GET', 'POST'])
def match(league_id, match_id):
    league = League.query.get_or_404(league_id)
    match = Match.query.get_or_404(match_id)
    league_completed = league.status == 'completed'
    round_completed = match.round.is_completed if match.round else False
    is_completed = league_completed or round_completed
    
    if request.method == 'POST':
        if is_completed:
            flash('Cannot change result. This round or league is completed.', 'error')
        elif not can_manage_league(league_id):
            flash('You do not have permission to manage this league', 'error')
        else:
            action = request.form.get('action')
            
            if action == 'cancel':
                match.status = 'cancelled'
                match.home_score = None
                match.away_score = None
                match.is_draw = False
                db.session.commit()
                flash('Match has been cancelled', 'success')
            
            elif action == 'walkover':
                winner = request.form.get('walkover_winner')
                if winner == '1':
                    match.home_score = 3
                    match.away_score = 0
                else:
                    match.home_score = 0
                    match.away_score = 3
                match.is_walkover = True
                match.walkover_winner = int(winner)
                match.status = 'walkover'
                match.played_at = datetime.utcnow()
                db.session.commit()
                flash('Walkover result saved!', 'success')
            
            else:
                home_score = request.form.get('home_score')
                away_score = request.form.get('away_score')
                
                if home_score is not None and away_score is not None:
                    match.home_score = int(home_score)
                    match.away_score = int(away_score)
                    match.is_draw = match.home_score == match.away_score
                    match.status = 'played'
                    match.played_at = datetime.utcnow()
                    db.session.commit()
                    flash('Match result saved!', 'success')
    
    can_manage = can_manage_league(league_id)
    return render_template('match.html', league=league, match=match, 
                           is_completed=is_completed, round_completed=round_completed,
                           can_manage=can_manage)

@main.route('/players')
def players():
    if session.get('is_admin'):
        all_players = Player.query.all()
    else:
        all_players = Player.query.filter_by(is_dummy=False).all()
    return render_template('players.html', players=all_players)

@main.route('/players/<int:player_id>')
def player(player_id):
    player = Player.query.get_or_404(player_id)
    
    # Hide dummy players from logged-in non-admin users
    if player.is_dummy and session.get('user_id') and not session.get('is_admin'):
        flash('Player not found', 'error')
        return redirect(url_for('main.players'))
    
    # All matches including cancelled (for history)
    all_matches = Match.query.filter(
        (Match.home_player_id == player_id) | (Match.away_player_id == player_id)
    ).order_by(Match.played_at.desc()).all()
    
    # Only played matches (for statistics) - exclude cancelled
    matches = [m for m in all_matches if m.home_score is not None and m.status != 'cancelled']
    
    # Next matches (where player is involved, no result yet, not cancelled, round is active)
    next_matches = Match.query.filter(
        ((Match.home_player_id == player_id) | (Match.away_player_id == player_id)) &
        (Match.home_score.is_(None)) &
        (Match.status != 'cancelled')
    ).join(LeagueRound).filter(
        LeagueRound.is_active == True
    ).order_by(LeagueRound.round_number).limit(3).all()
    
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
    
    if revenge_opportunities:
        latest = revenge_opportunities[0]
        revenge_opp = {
            'name': latest['opponent_name'],
            'score': latest['score']
        }
    else:
        revenge_opp = None
    
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
                          revenge_opp=revenge_opp,
                          next_matches=next_matches)

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
        
        if round_num == 0:
            league_round.is_active = True
        
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

@main.route('/tournaments')
def tournaments():
    all_tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
    return render_template('tournaments.html', tournaments=all_tournaments)

@main.route('/tournaments/create', methods=['GET', 'POST'])
def create_tournament():
    if not session.get('user_id'):
        flash('Please log in to create a tournament', 'error')
        return redirect(url_for('main.login'))
    
    games = Game.query.filter_by(allow_tournament=True, is_active=True).all()
    players = Player.query.all()
    
    pre_selected_game = request.args.get('game_id')
    
    if request.method == 'POST':
        name = request.form.get('name')
        game_id = request.form.get('game_id')
        format_type = request.form.get('format')
        best_of = request.form.get('best_of')
        selected_players = request.form.getlist('players')
        
        if not name or not game_id or not format_type:
            flash('Name, game, and format are required', 'error')
            return render_template('create_tournament.html', games=games, players=players)
        
        if len(selected_players) < 2:
            flash('At least 2 players are required', 'error')
            return render_template('create_tournament.html', games=games, players=players)
        
        tournament = Tournament(
            name=name,
            game_id=game_id,
            owner_id=session['user_id'],
            unique_id=uuid.uuid4().hex[:12],
            format=format_type,
            best_of=int(best_of) if best_of else 1
        )
        db.session.add(tournament)
        db.session.flush()
        
        for i, player_id in enumerate(selected_players):
            tp = TournamentPlayer(
                tournament_id=tournament.id,
                player_id=int(player_id),
                seed_number=i + 1
            )
            db.session.add(tp)
        
        db.session.commit()
        flash(f'Tournament "{name}" created successfully!', 'success')
        return redirect(url_for('main.tournament', tournament_id=tournament.id))
    
    return render_template('create_tournament.html', games=games, players=players, pre_selected_game=pre_selected_game)

@main.route('/tournaments/<int:tournament_id>')
def tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament_players = TournamentPlayer.query.filter_by(tournament_id=tournament_id).all()
    
    winners_matches = TournamentMatch.query.filter_by(
        tournament_id=tournament_id, bracket='winners'
    ).order_by(TournamentMatch.round_number, TournamentMatch.match_number).all()
    
    losers_matches = TournamentMatch.query.filter_by(
        tournament_id=tournament_id, bracket='losers'
    ).order_by(TournamentMatch.round_number, TournamentMatch.match_number).all()
    
    grand_finals = TournamentMatch.query.filter_by(
        tournament_id=tournament_id, bracket='grand_finals'
    ).first()
    
    matches_by_round = {}
    for match in winners_matches:
        if match.round_number not in matches_by_round:
            matches_by_round[match.round_number] = []
        matches_by_round[match.round_number].append(match)
    
    losers_matches_by_round = {}
    for match in losers_matches:
        if match.round_number not in losers_matches_by_round:
            losers_matches_by_round[match.round_number] = []
        losers_matches_by_round[match.round_number].append(match)
    
    can_manage = can_manage_tournament(tournament_id)
    
    own_profile = None
    if session.get('user_id'):
        player_exists = Player.query.filter_by(name=session.get('username')).first()
        if player_exists:
            own_profile = player_exists
    
    return render_template('tournament.html', 
                         tournament=tournament, 
                         tournament_players=tournament_players,
                         matches_by_round=matches_by_round,
                         losers_matches_by_round=losers_matches_by_round,
                         grand_finals=grand_finals,
                         can_manage=can_manage,
                         own_profile=own_profile)

@main.route('/tournaments/<int:tournament_id>/start', methods=['POST'])
def start_tournament(tournament_id):
    if not can_manage_tournament(tournament_id):
        flash('You do not have permission to manage this tournament', 'error')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    tournament = Tournament.query.get_or_404(tournament_id)
    
    if tournament.status != 'draft':
        flash('Tournament has already started', 'error')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    tournament_players = TournamentPlayer.query.filter_by(tournament_id=tournament_id).all()

@main.route('/tournaments/<int:tournament_id>/players')
def manage_tournament_players(tournament_id):
    if not can_manage_tournament(tournament_id):
        flash('You do not have permission to manage this tournament', 'error')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament_players = TournamentPlayer.query.filter_by(tournament_id=tournament_id).all()
    
    all_players = Player.query.all()
    current_player_ids = [tp.player_id for tp in tournament_players]
    
    available_players = [p for p in all_players if p.id not in current_player_ids]
    
    return render_template('manage_tournament_players.html',
                         tournament=tournament,
                         tournament_players=tournament_players,
                         available_players=available_players)

@main.route('/tournaments/<int:tournament_id>/players/add', methods=['POST'])
def add_tournament_player(tournament_id):
    if not can_manage_tournament(tournament_id):
        flash('You do not have permission to manage this tournament', 'error')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.status != 'draft':
        flash('Cannot add players - tournament has already started', 'error')
        return redirect(url_for('main.manage_tournament_players', tournament_id=tournament_id))
    
    player_id = request.form.get('player_id')
    if player_id:
        player_id = int(player_id)
        
        existing = TournamentPlayer.query.filter_by(
            tournament_id=tournament_id,
            player_id=player_id
        ).first()
        
        if not existing:
            max_seed = db.session.query(db.func.max(TournamentPlayer.seed_number)).filter_by(
                tournament_id=tournament_id
            ).scalar() or 0
            
            new_tp = TournamentPlayer(
                tournament_id=tournament_id,
                player_id=player_id,
                seed_number=max_seed + 1
            )
            db.session.add(new_tp)
            db.session.commit()
            flash('Player added successfully', 'success')
    
    return redirect(url_for('main.manage_tournament_players', tournament_id=tournament_id))

@main.route('/tournaments/<int:tournament_id>/request-join', methods=['POST'])
def request_join_tournament(tournament_id):
    if not session.get('user_id'):
        flash('Please log in to request to join', 'error')
        return redirect(url_for('main.login'))
    
    player_id = request.form.get('player_id')
    if not player_id:
        flash('No player selected', 'error')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    player_id = int(player_id)
    
    existing_request = TournamentJoinRequest.query.filter_by(
        tournament_id=tournament_id,
        player_id=player_id,
        status='pending'
    ).first()
    
    if existing_request:
        flash('You have already requested to join this tournament', 'info')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    already_in = TournamentPlayer.query.filter_by(
        tournament_id=tournament_id,
        player_id=player_id
    ).first()
    
    if already_in:
        flash('You are already in this tournament', 'info')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    join_request = TournamentJoinRequest(
        tournament_id=tournament_id,
        player_id=player_id,
        status='pending'
    )
    db.session.add(join_request)
    db.session.commit()
    flash('Join request sent!', 'success')
    return redirect(url_for('main.tournament', tournament_id=tournament_id))

@main.route('/tournaments/<int:tournament_id>/join-requests')
def view_tournament_join_requests(tournament_id):
    if not can_manage_tournament(tournament_id):
        flash('You do not have permission to view requests', 'error')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    tournament = Tournament.query.get_or_404(tournament_id)
    pending_requests = TournamentJoinRequest.query.filter_by(
        tournament_id=tournament_id,
        status='pending'
    ).all()
    
    return render_template('tournament_join_requests.html', tournament=tournament, pending_requests=pending_requests)

@main.route('/tournaments/<int:tournament_id>/join-requests/<int:request_id>/<action>', methods=['POST'])
def handle_tournament_join_request(tournament_id, request_id, action):
    if not can_manage_tournament(tournament_id):
        flash('You do not have permission to manage requests', 'error')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    join_request = TournamentJoinRequest.query.get_or_404(request_id)
    
    if action == 'approve':
        join_request.status = 'approved'
        tournament_player = TournamentPlayer(
            tournament_id=tournament_id,
            player_id=join_request.player_id,
            seed_number=None,
            eliminated=False
        )
        db.session.add(tournament_player)
        flash('Player added to tournament!', 'success')
    elif action == 'deny':
        join_request.status = 'denied'
        flash('Request denied', 'success')
    
    db.session.commit()
    return redirect(url_for('main.view_tournament_join_requests', tournament_id=tournament_id))

@main.route('/tournaments/<int:tournament_id>/players/remove/<int:player_id>', methods=['POST'])
def remove_tournament_player(tournament_id, player_id):
    if not can_manage_tournament(tournament_id):
        flash('You do not have permission to manage this tournament', 'error')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.status != 'draft':
        flash('Cannot remove players - tournament has already started', 'error')
        return redirect(url_for('main.manage_tournament_players', tournament_id=tournament_id))
    
    tournament_player = TournamentPlayer.query.filter_by(
        tournament_id=tournament_id,
        player_id=player_id
    ).first()
    
    if tournament_player:
        db.session.delete(tournament_player)
        db.session.commit()
        flash('Player removed successfully', 'success')
    
    return redirect(url_for('main.manage_tournament_players', tournament_id=tournament_id))
    player_count = len(tournament_players)
    
    if player_count < 2:
        flash('At least 2 players are required', 'error')
        return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    if tournament.format == 'single_elimination':
        generate_single_elimination_bracket(tournament, tournament_players)
    else:
        generate_double_elimination_bracket(tournament, tournament_players)
    
    tournament.status = 'active'
    tournament.started_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Tournament "{tournament.name}" has started!', 'success')
    return redirect(url_for('main.tournament', tournament_id=tournament_id))

@main.route('/tournaments/<int:tournament_id>/match/<int:match_id>', methods=['GET', 'POST'])
def tournament_match(tournament_id, match_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    match = TournamentMatch.query.get_or_404(match_id)
    
    can_manage = can_manage_tournament(tournament_id)
    is_completed = match.winner_id is not None
    
    if request.method == 'POST' and can_manage and not is_completed:
        score1 = request.form.get('score1')
        score2 = request.form.get('score2')
        
        if score1 is not None and score2 is not None:
            match.score1 = int(score1)
            match.score2 = int(score2)
            
            if match.score1 > match.score2:
                match.winner_id = match.player1_id
            elif match.score2 > match.score1:
                match.winner_id = match.player2_id
            
            match.played_at = datetime.utcnow()
            db.session.commit()
            
            advance_winner(match)
            
            if tournament.format == 'double_elimination' and match.bracket in ['winners', 'losers']:
                move_loser_to_losers_bracket(match)
            
            check_tournament_completion(tournament)
            
            flash('Match result saved!', 'success')
            return redirect(url_for('main.tournament', tournament_id=tournament_id))
    
    return render_template('tournament_match.html', tournament=tournament, match=match, can_manage=can_manage)

def generate_single_elimination_bracket(tournament, tournament_players):
    player_count = len(tournament_players)
    bracket_size = 1
    while bracket_size < player_count:
        bracket_size *= 2
    
    rounds = int(math.log2(bracket_size))
    matches_in_round = bracket_size // 2
    
    first_round_matches = []
    for i in range(matches_in_round):
        match = TournamentMatch(
            tournament_id=tournament.id,
            bracket='winners',
            round_number=1,
            match_number=i + 1
        )
        db.session.add(match)
        db.session.flush()
        first_round_matches.append(match)
    
    for i, tp in enumerate(tournament_players[:bracket_size]):
        match_idx = i // 2
        if i % 2 == 0:
            first_round_matches[match_idx].player1_id = tp.player_id
        else:
            first_round_matches[match_idx].player2_id = tp.player_id
    
    for i in range(matches_in_round):
        if first_round_matches[i].player1_id and first_round_matches[i].player2_id:
            continue
        elif first_round_matches[i].player1_id:
            first_round_matches[i].winner_id = first_round_matches[i].player1_id
            first_round_matches[i].is_bye = True
        elif first_round_matches[i].player2_id:
            first_round_matches[i].winner_id = first_round_matches[i].player2_id
            first_round_matches[i].is_bye = True
    
    next_match_idx = 0
    for round_num in range(2, rounds + 1):
        matches_in_round = bracket_size // (2 ** round_num)
        round_matches = []
        for i in range(matches_in_round):
            match = TournamentMatch(
                tournament_id=tournament.id,
                bracket='winners',
                round_number=round_num,
                match_number=i + 1
            )
            db.session.add(match)
            db.session.flush()
            round_matches.append(match)
        
        for i in range(matches_in_round):
            match1_idx = next_match_idx + i * 2
            match2_idx = next_match_idx + i * 2 + 1
            
            prev_match1 = first_round_matches[match1_idx] if round_num == 2 else round_matches[(i * 2)]
            prev_match2 = first_round_matches[match2_idx] if round_num == 2 else round_matches[(i * 2) + 1]
            
            round_matches[i].next_match_id = None
        
        first_round_matches = round_matches
        next_match_idx = 0
    
    link_matches_in_bracket(tournament, 'winners')

def generate_double_elimination_bracket(tournament, tournament_players):
    player_count = len(tournament_players)
    bracket_size = 1
    while bracket_size < player_count:
        bracket_size *= 2
    
    winners_rounds = int(math.log2(bracket_size))
    losers_rounds = winners_rounds * 2 - 1
    
    generate_single_elimination_bracket(tournament, tournament_players)
    
    for round_num in range(1, losers_rounds + 1):
        matches_in_round = bracket_size // (2 ** ((round_num + 1) // 2 + 1))
        if matches_in_round < 1:
            matches_in_round = 1
        
        for i in range(matches_in_round):
            match = TournamentMatch(
                tournament_id=tournament.id,
                bracket='losers',
                round_number=round_num,
                match_number=i + 1
            )
            db.session.add(match)
    
    grand_finals = TournamentMatch(
        tournament_id=tournament.id,
        bracket='grand_finals',
        round_number=1,
        match_number=1
    )
    db.session.add(grand_finals)
    
    link_matches_in_bracket(tournament, 'winners')
    link_matches_in_bracket(tournament, 'losers')

def link_matches_in_bracket(tournament, bracket_type):
    matches = TournamentMatch.query.filter_by(
        tournament_id=tournament.id, bracket=bracket_type
    ).order_by(TournamentMatch.round_number, TournamentMatch.match_number).all()
    
    if not matches:
        return
    
    rounds = {}
    for match in matches:
        if match.round_number not in rounds:
            rounds[match.round_number] = []
        rounds[match.round_number].append(match)
    
    for round_num in sorted(rounds.keys())[:-1]:
        current_round = rounds[round_num]
        next_round = rounds[round_num + 1]
        
        for i, match in enumerate(current_round):
            if len(next_round) > i // 2:
                match.next_match_id = next_round[i // 2].id

def advance_winner(match):
    if not match.next_match_id:
        return
    
    next_match = TournamentMatch.query.get(match.next_match_id)
    if not next_match:
        return
    
    if next_match.player1_id is None:
        next_match.player1_id = match.winner_id
    elif next_match.player2_id is None:
        next_match.player2_id = match.winner_id
    
    db.session.commit()

def move_loser_to_losers_bracket(match):
    if not match.loser_next_match_id:
        return
    
    loser_id = match.player1_id if match.winner_id == match.player2_id else match.player2_id
    if not loser_id:
        return
    
    loser_match = TournamentMatch.query.get(match.loser_next_match_id)
    if not loser_match:
        return
    
    if loser_match.player1_id is None:
        loser_match.player1_id = loser_id
    elif loser_match.player2_id is None:
        loser_match.player2_id = loser_id
    
    db.session.commit()

def check_tournament_completion(tournament):
    if tournament.status != 'active':
        return
    
    if tournament.format == 'single_elimination':
        final_match = TournamentMatch.query.filter_by(
            tournament_id=tournament.id, bracket='winners'
        ).order_by(TournamentMatch.round_number.desc()).first()
        
        if final_match and final_match.winner_id:
            tournament.status = 'completed'
            tournament.ended_at = datetime.utcnow()
            
            winner_tp = TournamentPlayer.query.filter_by(
                tournament_id=tournament.id, player_id=final_match.winner_id
            ).first()
            if winner_tp:
                winner_tp.placement = 1
            
            db.session.commit()
    else:
        grand_finals = TournamentMatch.query.filter_by(
            tournament_id=tournament.id, bracket='grand_finals'
        ).first()
        
        if grand_finals and grand_finals.winner_id:
            tournament.status = 'completed'
            tournament.ended_at = datetime.utcnow()
            
            winner_tp = TournamentPlayer.query.filter_by(
                tournament_id=tournament.id, player_id=grand_finals.winner_id
            ).first()
            if winner_tp:
                winner_tp.placement = 1
            
            db.session.commit()

@main.route('/leagues/<int:league_id>/ffa/create', methods=['GET', 'POST'])
def create_ffa_in_league(league_id):
    if not can_manage_league(league_id):
        flash('You do not have permission to manage this league', 'error')
        return redirect(url_for('main.league', league_id=league_id))
    
    league = League.query.get_or_404(league_id)
    games = Game.query.filter_by(allow_league=True, is_active=True).all()
    players = Player.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        game_id = request.form.get('game_id')
        selected_players = request.form.getlist('players')
        
        if not name or not game_id:
            flash('Name and game are required', 'error')
            return render_template('create_ffa.html', league=league, games=games, players=players)
        
        if len(selected_players) < 2:
            flash('At least 2 players required', 'error')
            return render_template('create_ffa.html', league=league, games=games, players=players)
        
        ffa = FFAMatch(
            league_id=league_id,
            name=name,
            game_id=game_id,
            status='active'
        )
        db.session.add(ffa)
        db.session.flush()
        
        for i, player_id in enumerate(selected_players):
            fp = FFAPlayer(
                ffa_match_id=ffa.id,
                player_id=int(player_id)
            )
            db.session.add(fp)
        
        db.session.commit()
        flash(f'FFA match "{name}" created!', 'success')
        return redirect(url_for('main.league', league_id=league_id))
    
    return render_template('create_ffa.html', league=league, games=games, players=players)

@main.route('/ffa/create', methods=['GET', 'POST'])
def create_ffa():
    if not session.get('user_id'):
        flash('Please log in to create FFA', 'error')
        return redirect(url_for('main.login'))
    
    games = Game.query.filter_by(is_active=True).all()
    players = Player.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        game_id = request.form.get('game_id')
        selected_players = request.form.getlist('players')
        
        if not name or not game_id:
            flash('Name and game are required', 'error')
            return render_template('create_ffa.html', games=games, players=players)
        
        if len(selected_players) < 2:
            flash('At least 2 players required', 'error')
            return render_template('create_ffa.html', games=games, players=players)
        
        ffa = FFAMatch(
            league_id=None,
            name=name,
            game_id=game_id,
            owner_id=session['user_id'],
            status='active'
        )
        db.session.add(ffa)
        db.session.flush()
        
        for player_id in selected_players:
            fp = FFAPlayer(
                ffa_match_id=ffa.id,
                player_id=int(player_id)
            )
            db.session.add(fp)
        
        db.session.commit()
        flash(f'FFA "{name}" created!', 'success')
        return redirect(url_for('main.ffa_match', ffa_id=ffa.id))
    
    return render_template('create_ffa.html', games=games, players=players)

@main.route('/ffa')
def ffa_list():
    ffAs = FFAMatch.query.filter_by(league_id=None).order_by(FFAMatch.created_at.desc()).all()
    return render_template('ffa_list.html', ffAs=ffAs)

@main.route('/ffa/<int:ffa_id>', methods=['GET', 'POST'])
def ffa_match(ffa_id):
    ffa = FFAMatch.query.get_or_404(ffa_id)
    can_manage = can_manage_ffa(ffa_id)
    ffa_players = FFAPlayer.query.filter_by(ffa_match_id=ffa_id).order_by(FFAPlayer.placement).all()
    all_players = Player.query.all()
    
    # Get players not yet in FFA (for adding more)
    current_player_ids = [fp.player_id for fp in ffa_players]
    available_to_add = [p for p in all_players if p.id not in current_player_ids]
    
    if request.method == 'POST' and can_manage and ffa.status == 'active':
        for fp in ffa_players:
            placement_key = f'placement_{fp.player_id}'
            placement = request.form.get(placement_key)
            if placement:
                fp.placement = int(placement)
                # Poengberegning: 1. plass får floor(X/2), alle andre får 1 poeng
                player_count = len(ffa_players)
                if fp.placement == 1:
                    fp.points_earned = player_count // 2
                else:
                    fp.points_earned = 1
        
        ffa.status = 'completed'
        ffa.played_at = datetime.utcnow()
        db.session.commit()
        flash('FFA result saved!', 'success')
        return redirect(url_for('main.ffa_match', ffa_id=ffa_id))
    
    return render_template('ffa_match.html', ffa=ffa, ffa_players=ffa_players, can_manage=can_manage, available_to_add=available_to_add)

import math
