"""
Flask API Server for AllFence Fencing Management System
Serves REST endpoints for tournaments, fencers, and rankings
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from datetime import datetime, date

from src.database import DATABASE_URL, init_db, get_session_context
from src.models import Club, Fencer, Ranking, Tournament, TournamentResult, User, Season, Base
from src.enums import WeaponType, AgeBracket, Gender, CompetitionType, TournamentStatus, ClubStatus
from src.auth import generate_token, require_auth, require_admin
from src.ranking import eligible_brackets
from src.season_simulation import simulate_full_season

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Get configuration from environment
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

# CORS configuration - restrict in production
cors_origins = os.getenv('CORS_ORIGINS', '*')
if cors_origins == '*':
    logger.warning("CORS is set to allow all origins. Set CORS_ORIGINS environment variable for production.")
    CORS(app)
else:
    allowed_origins = [origin.strip() for origin in cors_origins.split(',')]
    CORS(app, origins=allowed_origins)
    logger.info(f"CORS enabled for origins: {allowed_origins}")

# Database setup
init_db()  # Initialize tables


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        with get_session_context() as db:
            user = db.query(User).filter(User.username == username).first()
            
            if not user or not user.check_password(password):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            token = generate_token(user.user_id, user.username, user.is_admin)
            
            return jsonify({
                'token': token,
                'user': user.to_dict()
            }), 200
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user(user_data):
    """Get current authenticated user info"""
    try:
        with get_session_context() as db:
            user = db.query(User).filter(User.user_id == user_data['user_id']).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify(user.to_dict()), 200
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user (open endpoint for demo - restrict in production!)"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password required'}), 400
        
        with get_session_context() as db:
            # Check if user exists
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return jsonify({'error': 'Username or email already exists'}), 400
            
            # Create new user
            user = User(username=username, email=email, is_admin=False)
            user.set_password(password)
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            token = generate_token(user.user_id, user.username, user.is_admin)
            
            return jsonify({
                'token': token,
                'user': user.to_dict()
            }), 201
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# TOURNAMENTS ENDPOINTS
# ============================================================================

@app.route('/api/tournaments', methods=['GET'])
def get_tournaments():
    """Get all tournaments with optional filters"""
    try:
        with get_session_context() as db:
            query = db.query(Tournament)
            
            # Apply filters
            status = request.args.get('status')
            if status:
                query = query.filter(Tournament.status == status)
            
            weapon = request.args.get('weapon')
            if weapon:
                query = query.filter(Tournament.weapon == weapon)
            
            bracket = request.args.get('bracket')
            if bracket:
                query = query.filter(Tournament.bracket == bracket)
            
            search = request.args.get('search')
            if search:
                query = query.filter(Tournament.tournament_name.ilike(f'%{search}%'))
            
            # Order by date (soonest first)
            query = query.order_by(Tournament.date.asc())
            
            tournaments = query.all()
            return jsonify([t.to_dict() for t in tournaments]), 200
    except Exception as e:
        logger.error(f"Error getting tournaments: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tournaments/<int:tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    """Get single tournament by ID"""
    try:
        with get_session_context() as db:
            tournament = db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()
            if not tournament:
                return jsonify({'error': 'Tournament not found'}), 404
            return jsonify(tournament.to_dict()), 200
    except Exception as e:
        logger.error(f"Error getting tournament: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tournaments', methods=['POST'])
def create_tournament():
    """Create a new tournament"""
    try:
        data = request.json
        with get_session_context() as db:
            tournament = Tournament(
                tournament_name=data.get('tournament_name'),
                date=data.get('date'),
                weapon=data.get('weapon'),
                bracket=data.get('bracket'),
                competition_type=data.get('competition_type'),
                gender=data.get('gender'),
                location=data.get('location'),
                max_participants=data.get('max_participants'),
                description=data.get('description'),
                status=TournamentStatus.UPCOMING
            )
            db.add(tournament)
            db.commit()
            return jsonify(tournament.to_dict()), 201
    except Exception as e:
        logger.error(f"Error creating tournament: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tournaments/<int:tournament_id>', methods=['PUT'])
@require_admin
def update_tournament(tournament_id, user_data):
    """Update tournament information (admin only)"""
    try:
        data = request.get_json()
        with get_session_context() as db:
            tournament = db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()
            if not tournament:
                return jsonify({'error': 'Tournament not found'}), 404
            
            # Update fields if provided
            if 'tournament_name' in data:
                tournament.tournament_name = data['tournament_name']
            if 'date' in data:
                date_str = data['date']
                if isinstance(date_str, str):
                    tournament.date = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:
                    tournament.date = date_str
            if 'weapon' in data:
                tournament.weapon = data['weapon']
            if 'bracket' in data:
                tournament.bracket = data['bracket']
            if 'competition_type' in data:
                tournament.competition_type = data['competition_type']
            if 'gender' in data:
                tournament.gender = data['gender']
            if 'location' in data:
                tournament.location = data['location']
            if 'max_participants' in data:
                tournament.max_participants = data['max_participants']
            if 'description' in data:
                tournament.description = data['description']
            if 'status' in data:
                tournament.status = data['status']
            
            db.commit()
            db.refresh(tournament)
            
            return jsonify(tournament.to_dict()), 200
    except Exception as e:
        logger.error(f"Error updating tournament: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tournaments/<int:tournament_id>/register', methods=['POST'])
@require_admin
def register_fencer(tournament_id, user_data):
    """Register a fencer for a tournament (admin only)"""
    try:
        data = request.get_json()
        fencer_id = data.get('fencer_id')
        
        if not fencer_id:
            return jsonify({'error': 'fencer_id is required'}), 400
        
        with get_session_context() as db:
            # Check if tournament exists
            tournament = db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()
            if not tournament:
                return jsonify({'error': 'Tournament not found'}), 404
            
            # Check if fencer exists
            fencer = db.query(Fencer).filter(Fencer.fencer_id == fencer_id).first()
            if not fencer:
                return jsonify({'error': 'Fencer not found'}), 404
            
            # Check if fencer is already registered
            existing = db.query(TournamentResult).filter(
                TournamentResult.tournament_id == tournament_id,
                TournamentResult.fencer_id == fencer_id
            ).first()
            
            if existing:
                return jsonify({'error': 'Fencer already registered for this tournament'}), 400
            
            # Create tournament result with placement = 0 (not yet competed)
            result = TournamentResult(
                tournament_id=tournament_id,
                fencer_id=fencer_id,
                placement=0,
                points_awarded=0
            )
            db.add(result)
            db.commit()
            
            return jsonify({'message': 'Fencer registered successfully'}), 201
    except Exception as e:
        logger.error(f"Error registering fencer: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tournaments/<int:tournament_id>/participants', methods=['GET'])
def get_tournament_participants(tournament_id):
    """Get all participants registered for a tournament"""
    try:
        with get_session_context() as db:
            # Get all results for this tournament
            results = db.query(TournamentResult).filter(
                TournamentResult.tournament_id == tournament_id
            ).all()
            
            participants = []
            for result in results:
                fencer = result.fencer
                if fencer:
                    participant_data = {
                        'result_id': result.result_id,
                        'fencer_id': fencer.fencer_id,
                        'full_name': fencer.full_name,
                        'club_name': fencer.club.club_name if fencer.club else None,
                        'weapon': fencer.weapon,
                        'placement': result.placement if result.placement > 0 else None,
                        'points_awarded': result.points_awarded,
                        'pool_record': result.pool_record,
                        'seeding': result.seeding
                    }
                    participants.append(participant_data)
            
            return jsonify(participants), 200
    except Exception as e:
        logger.error(f"Error getting tournament participants: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tournaments/<int:tournament_id>/participants/<int:fencer_id>', methods=['DELETE'])
@require_admin
def unregister_fencer(tournament_id, fencer_id, user_data):
    """Remove a fencer from tournament registration (admin only)"""
    try:
        with get_session_context() as db:
            # Find the tournament result record
            result = db.query(TournamentResult).filter(
                TournamentResult.tournament_id == tournament_id,
                TournamentResult.fencer_id == fencer_id
            ).first()
            
            if not result:
                return jsonify({'error': 'Participant not found'}), 404
            
            # Don't allow deletion if results have been recorded
            if result.placement > 0:
                return jsonify({'error': 'Cannot remove participant with recorded results'}), 400
            
            db.delete(result)
            db.commit()
            
            return jsonify({'message': 'Participant removed successfully'}), 200
    except Exception as e:
        logger.error(f"Error removing participant: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tournaments/<int:tournament_id>/results', methods=['POST'])
@require_admin
def record_tournament_results(tournament_id, user_data):
    """Record results for a tournament and update rankings (admin only)"""
    try:
        data = request.get_json()
        results = data.get('results', [])  # List of {fencer_id, placement}
        
        if not results:
            return jsonify({'error': 'Results array is required'}), 400
        
        with get_session_context() as db:
            # Check if tournament exists
            tournament = db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()
            if not tournament:
                return jsonify({'error': 'Tournament not found'}), 404
            
            # Import here to avoid circular imports
            from src.tournament_points import calculate_points
            
            updated_count = 0
            errors = []
            
            for result_data in results:
                fencer_id = result_data.get('fencer_id')
                placement = result_data.get('placement')
                
                if not fencer_id or placement is None:
                    errors.append(f"Missing fencer_id or placement in result: {result_data}")
                    continue
                
                # Find the tournament result record
                tournament_result = db.query(TournamentResult).filter(
                    TournamentResult.tournament_id == tournament_id,
                    TournamentResult.fencer_id == fencer_id
                ).first()
                
                if not tournament_result:
                    errors.append(f"Fencer {fencer_id} is not registered for this tournament")
                    continue
                
                # Calculate points based on placement and competition type
                points = calculate_points(placement, tournament.competition_type)
                
                # Update tournament result
                tournament_result.placement = placement
                tournament_result.points_awarded = points
                
                # Update or create ranking for this fencer's weapon/bracket
                fencer = tournament_result.fencer
                age = (date.today() - fencer.dob).days // 365
                current_bracket = eligible_brackets(age)[-1] if eligible_brackets(age) else None
                
                if current_bracket:
                    ranking = db.query(Ranking).filter(
                        Ranking.fencer_id == fencer_id,
                        Ranking.bracket_name == current_bracket
                    ).first()
                    
                    if ranking:
                        # Update existing ranking
                        ranking.points += points
                    else:
                        # Create new ranking
                        ranking = Ranking(
                            fencer_id=fencer_id,
                            bracket_name=current_bracket,
                            points=points
                        )
                        db.add(ranking)
                
                updated_count += 1
            
            # Commit all changes
            db.commit()
            
            # Recalculate ranks for affected brackets
            # Get unique brackets that were affected
            affected_brackets = set()
            for result_data in results:
                fencer_id = result_data.get('fencer_id')
                if fencer_id:
                    fencer = db.query(Fencer).filter(Fencer.fencer_id == fencer_id).first()
                    if fencer:
                        age = (date.today() - fencer.dob).days // 365
                        current_bracket = eligible_brackets(age)[-1] if eligible_brackets(age) else None
                        if current_bracket:
                            affected_brackets.add(current_bracket)
            
            # Recalculate ranks for each affected bracket
            # Note: Rankings are per bracket only, not per weapon/bracket combination
            for bracket in affected_brackets:
                rankings = db.query(Ranking).filter(
                    Ranking.bracket_name == bracket
                ).order_by(Ranking.points.desc()).all()
                
                # Rankings are ordered by points, no explicit rank field to update
            
            db.commit()
            
            response = {
                'message': 'Results recorded successfully',
                'updated_count': updated_count,
                'errors': errors if errors else None
            }
            
            return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error recording tournament results: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# FENCERS ENDPOINTS
# ============================================================================

@app.route('/api/fencers', methods=['GET'])
def get_fencers():
    """Get all fencers with optional filters"""
    try:
        with get_session_context() as db:
            query = db.query(Fencer)
            
            # Apply filters
            weapon = request.args.get('weapon')
            if weapon:
                query = query.filter(Fencer.weapon == weapon)
            
            gender = request.args.get('gender')
            if gender:
                query = query.filter(Fencer.gender == gender)
            
            club_id = request.args.get('club_id')
            if club_id:
                query = query.filter(Fencer.club_id == club_id)
            
            search = request.args.get('search')
            if search:
                query = query.filter(Fencer.full_name.ilike(f'%{search}%'))
            
            # Get all fencers (no limit for registration purposes)
            fencers = query.all()
            
            # Apply bracket filter in Python (since bracket is computed from age)
            bracket = request.args.get('bracket')
            if bracket:
                from src.ranking import calculate_age, eligible_brackets
                fencers = [f for f in fencers if bracket in eligible_brackets(calculate_age(f.dob))]
            
            return jsonify([f.to_dict() for f in fencers]), 200
    except Exception as e:
        logger.error(f"Error getting fencers: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fencers/<int:fencer_id>', methods=['GET'])
def get_fencer(fencer_id):
    """Get single fencer by ID"""
    try:
        with get_session_context() as db:
            fencer = db.query(Fencer).filter(Fencer.fencer_id == fencer_id).first()
            if not fencer:
                return jsonify({'error': 'Fencer not found'}), 404
            return jsonify(fencer.to_dict()), 200
    except Exception as e:
        logger.error(f"Error getting fencer: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fencers/<int:fencer_id>', methods=['PUT'])
@require_admin
def update_fencer(fencer_id, user_data):
    """Update fencer information (admin only)"""
    try:
        data = request.get_json()
        with get_session_context() as db:
            fencer = db.query(Fencer).filter(Fencer.fencer_id == fencer_id).first()
            if not fencer:
                return jsonify({'error': 'Fencer not found'}), 404
            
            # Update fields if provided
            if 'first_name' in data:
                fencer.first_name = data['first_name']
            if 'last_name' in data:
                fencer.last_name = data['last_name']
            if 'dob' in data:
                # Convert string date to date object
                dob_str = data['dob']
                if isinstance(dob_str, str):
                    fencer.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                else:
                    fencer.dob = dob_str
            if 'gender' in data:
                fencer.gender = data['gender']
            if 'weapon' in data:
                fencer.weapon = data['weapon']
            if 'club_id' in data:
                fencer.club_id = data['club_id']
            
            db.commit()
            db.refresh(fencer)
            
            return jsonify(fencer.to_dict()), 200
    except Exception as e:
        logger.error(f"Error updating fencer: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fencers/<int:fencer_id>/rankings', methods=['GET'])
def get_fencer_rankings(fencer_id):
    """Get rankings for a specific fencer"""
    try:
        with get_session_context() as db:
            rankings = db.query(Ranking).filter(Ranking.fencer_id == fencer_id).all()
            return jsonify([r.to_dict() for r in rankings]), 200
    except Exception as e:
        logger.error(f"Error getting fencer rankings: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fencers/<int:fencer_id>/results', methods=['GET'])
def get_fencer_tournament_results(fencer_id):
    """Get all tournament results for a specific fencer"""
    try:
        with get_session_context() as db:
            results = db.query(TournamentResult).filter(
                TournamentResult.fencer_id == fencer_id,
                TournamentResult.placement > 0  # Only results with recorded placements
            ).all()
            
            results_data = []
            for result in results:
                tournament = result.tournament
                if tournament:
                    results_data.append({
                        'result_id': result.result_id,
                        'tournament_id': tournament.tournament_id,
                        'tournament_name': tournament.tournament_name,
                        'date': tournament.date.isoformat() if tournament.date else None,
                        'competition_type': tournament.competition_type,
                        'placement': result.placement,
                        'points_awarded': result.points_awarded,
                        'weapon': tournament.weapon,
                        'bracket': tournament.bracket
                    })
            
            # Sort by date descending (most recent first)
            results_data.sort(key=lambda x: x['date'], reverse=True)
            
            return jsonify(results_data), 200
    except Exception as e:
        logger.error(f"Error getting fencer tournament results: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fencers/<int:fencer_id>/upcoming-tournaments', methods=['GET'])
def get_fencer_upcoming_tournaments(fencer_id):
    """Get eligible upcoming tournaments for a fencer"""
    try:
        with get_session_context() as db:
            # Get fencer info
            fencer = db.query(Fencer).filter(Fencer.fencer_id == fencer_id).first()
            if not fencer:
                return jsonify({'error': 'Fencer not found'}), 404
            
            # Calculate age and bracket
            age = (date.today() - fencer.dob).days // 365
            current_bracket = eligible_brackets(age)[-1] if eligible_brackets(age) else None
            
            if not current_bracket:
                return jsonify([]), 200
            
            # Get upcoming tournaments that match fencer's weapon and bracket
            # and are not yet completed
            upcoming_tournaments = db.query(Tournament).filter(
                Tournament.weapon == fencer.weapon,
                Tournament.bracket == current_bracket,
                Tournament.date >= date.today(),
                Tournament.status.in_([TournamentStatus.UPCOMING, TournamentStatus.REGISTRATION_OPEN, TournamentStatus.IN_PROGRESS])
            ).order_by(Tournament.date.asc()).all()
            
            # Check which tournaments the fencer is registered for
            tournament_data = []
            for tournament in upcoming_tournaments:
                # Check if fencer is registered
                registration = db.query(TournamentResult).filter(
                    TournamentResult.tournament_id == tournament.tournament_id,
                    TournamentResult.fencer_id == fencer_id
                ).first()
                
                tournament_data.append({
                    'tournament_id': tournament.tournament_id,
                    'tournament_name': tournament.tournament_name,
                    'date': tournament.date.isoformat() if tournament.date else None,
                    'competition_type': tournament.competition_type,
                    'status': tournament.status,
                    'location': tournament.location,
                    'is_registered': registration is not None,
                    'weapon': tournament.weapon,
                    'bracket': tournament.bracket,
                    'gender': tournament.gender
                })
            
            return jsonify(tournament_data), 200
    except Exception as e:
        logger.error(f"Error getting fencer upcoming tournaments: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# RANKINGS ENDPOINTS
# ============================================================================

@app.route('/api/rankings', methods=['GET'])
def get_rankings():
    """Get rankings with optional bracket and weapon filters"""
    try:
        with get_session_context() as db:
            query = db.query(Ranking).join(Fencer, Ranking.fencer_id == Fencer.fencer_id)
            
            bracket = request.args.get('bracket')
            if bracket:
                query = query.filter(Ranking.bracket_name == bracket)
            
            weapon = request.args.get('weapon')
            if weapon:
                query = query.filter(Fencer.weapon == weapon)
            
            # Sort by points descending
            rankings = query.order_by(Ranking.points.desc()).all()
            
            # Include fencer information in the response
            result = []
            for r in rankings:
                ranking_dict = r.to_dict()
                if r.fencer:
                    ranking_dict['fencer'] = r.fencer.to_dict(include_rankings=False)
                result.append(ranking_dict)
            
            return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting rankings: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rankings/clubs', methods=['GET'])
def get_club_rankings():
    """Get club rankings by weapon - aggregates points from all club fencers"""
    try:
        with get_session_context() as db:
            # Optional weapon filter
            weapon = request.args.get('weapon')
            
            # Query to aggregate club rankings
            from sqlalchemy import func
            
            query = db.query(
                Club.club_id,
                Club.club_name,
                Club.weapon_club,
                func.sum(Ranking.points).label('total_points'),
                func.count(func.distinct(Fencer.fencer_id)).label('fencer_count'),
                func.avg(Ranking.points).label('avg_points')
            ).select_from(Club).join(
                Fencer, Club.club_id == Fencer.club_id
            ).join(
                Ranking, Fencer.fencer_id == Ranking.fencer_id
            )
            
            # Filter by weapon if specified
            if weapon:
                query = query.filter(Fencer.weapon == weapon)
            
            # Group by club
            query = query.group_by(
                Club.club_id,
                Club.club_name,
                Club.weapon_club
            )
            
            # Order by total points descending
            query = query.order_by(func.sum(Ranking.points).desc())
            
            results = query.all()
            
            # Format response
            club_rankings = []
            for idx, result in enumerate(results, start=1):
                club_rankings.append({
                    'rank': idx,
                    'club_id': result.club_id,
                    'club_name': result.club_name,
                    'weapon_specialization': result.weapon_club if result.weapon_club else 'Mixed',
                    'total_points': int(result.total_points) if result.total_points else 0,
                    'fencer_count': result.fencer_count,
                    'avg_points': round(float(result.avg_points), 2) if result.avg_points else 0.0
                })
            
            return jsonify(club_rankings), 200
    except Exception as e:
        logger.error(f"Error getting club rankings: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rankings/cumulative-points', methods=['GET'])
def get_top_fencers_cumulative_points():
    """Get cumulative points over time for top 10 fencers in a bracket"""
    try:
        with get_session_context() as db:
            bracket = request.args.get('bracket')
            weapon = request.args.get('weapon')
            limit = int(request.args.get('limit', 10))
            
            if not bracket:
                return jsonify({'error': 'bracket parameter is required'}), 400
            
            from sqlalchemy import func
            
            # Get top N fencers in this bracket
            top_fencers_query = db.query(Ranking).join(
                Fencer, Ranking.fencer_id == Fencer.fencer_id
            ).filter(
                Ranking.bracket_name == bracket
            )
            
            if weapon:
                top_fencers_query = top_fencers_query.filter(Fencer.weapon == weapon)
            
            top_fencers = top_fencers_query.order_by(
                Ranking.points.desc()
            ).limit(limit).all()
            
            # For each top fencer, get their cumulative points over time
            all_fencers_data = []
            
            for ranking in top_fencers:
                fencer = ranking.fencer
                if not fencer:
                    continue
                
                # Get tournament results for this fencer in this bracket, sorted by date
                results = db.query(
                    Tournament.date,
                    Tournament.tournament_name,
                    TournamentResult.points_awarded
                ).select_from(TournamentResult).join(
                    Tournament, TournamentResult.tournament_id == Tournament.tournament_id
                ).filter(
                    TournamentResult.fencer_id == fencer.fencer_id,
                    Tournament.bracket == bracket,
                    Tournament.status == 'Completed',
                    TournamentResult.points_awarded > 0
                ).order_by(
                    Tournament.date
                ).all()
                
                # Calculate cumulative points
                cumulative_data = []
                cumulative_total = 0
                
                for result in results:
                    cumulative_total += result.points_awarded
                    cumulative_data.append({
                        'date': result.date.strftime('%Y-%m-%d') if result.date else None,
                        'tournament_name': result.tournament_name,
                        'points_awarded': result.points_awarded,
                        'cumulative_points': cumulative_total
                    })
                
                if cumulative_data:  # Only include fencers that have tournament data
                    all_fencers_data.append({
                        'fencer_id': fencer.fencer_id,
                        'fencer_name': fencer.full_name,
                        'current_points': ranking.points,
                        'data': cumulative_data
                    })
            
            return jsonify(all_fencers_data), 200
    except Exception as e:
        logger.error(f"Error getting cumulative points for top fencers: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rankings/clubs/cumulative-points', methods=['GET'])
def get_all_clubs_cumulative_points():
    """Get cumulative points over time for all clubs in a weapon category"""
    try:
        with get_session_context() as db:
            weapon = request.args.get('weapon')
            
            if not weapon:
                return jsonify({'error': 'weapon parameter is required'}), 400
            
            from sqlalchemy import func
            
            # Get all clubs with their fencers in this weapon
            clubs_query = db.query(
                Club.club_id,
                Club.club_name
            ).join(
                Fencer, Club.club_id == Fencer.club_id
            ).filter(
                Fencer.weapon == weapon
            ).group_by(
                Club.club_id,
                Club.club_name
            ).all()
            
            # For each club, get their cumulative points over time
            all_clubs_data = []
            
            for club in clubs_query:
                # Get tournament results for this club's fencers in this weapon
                results = db.query(
                    Tournament.date,
                    Tournament.tournament_name,
                    func.sum(TournamentResult.points_awarded).label('points')
                ).select_from(TournamentResult).join(
                    Tournament, TournamentResult.tournament_id == Tournament.tournament_id
                ).join(
                    Fencer, TournamentResult.fencer_id == Fencer.fencer_id
                ).filter(
                    Fencer.club_id == club.club_id,
                    Fencer.weapon == weapon,
                    Tournament.status == 'Completed'
                ).group_by(
                    Tournament.date,
                    Tournament.tournament_name,
                    Tournament.tournament_id
                ).order_by(
                    Tournament.date
                ).all()
                
                # Calculate cumulative points
                cumulative_data = []
                cumulative_total = 0
                
                for result in results:
                    cumulative_total += result.points
                    cumulative_data.append({
                        'date': result.date.strftime('%Y-%m-%d') if result.date else None,
                        'cumulative_points': cumulative_total
                    })
                
                if cumulative_data:  # Only include clubs that have tournament data
                    all_clubs_data.append({
                        'club_id': club.club_id,
                        'club_name': club.club_name,
                        'data': cumulative_data
                    })
            
            return jsonify(all_clubs_data), 200
    except Exception as e:
        logger.error(f"Error getting cumulative points for all clubs: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# CLUBS ENDPOINTS
# ============================================================================

@app.route('/api/clubs', methods=['GET'])
def get_clubs():
    """Get all clubs"""
    try:
        with get_session_context() as db:
            clubs = db.query(Club).all()
            return jsonify([c.to_dict() for c in clubs]), 200
    except Exception as e:
        logger.error(f"Error getting clubs: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/clubs/<string:club_id>', methods=['GET'])
def get_club_by_id(club_id):
    """Get club details with all members and statistics"""
    try:
        with get_session_context() as db:
            club = db.query(Club).filter_by(club_id=club_id).first()
            
            if not club:
                return jsonify({'error': 'Club not found'}), 404
            
            # Get club basic info
            club_data = club.to_dict()
            
            # Get all fencers with their rankings
            fencers_data = []
            weapon_counts = {'Sabre': 0, 'Foil': 0, 'Epee': 0}
            bracket_counts = {}
            total_points = 0
            
            for fencer in club.fencers:
                # Count weapons
                if fencer.weapon in weapon_counts:
                    weapon_counts[fencer.weapon] += 1
                
                # Get fencer's total points
                fencer_points = 0
                fencer_brackets = []
                for ranking in fencer.rankings:
                    fencer_points += ranking.points
                    fencer_brackets.append(ranking.bracket_name)
                    # Count brackets
                    bracket_counts[ranking.bracket_name] = bracket_counts.get(ranking.bracket_name, 0) + 1
                
                total_points += fencer_points
                
                fencers_data.append({
                    'fencer_id': fencer.fencer_id,
                    'full_name': fencer.full_name,
                    'dob': fencer.dob.strftime('%Y-%m-%d') if fencer.dob else None,
                    'gender': fencer.gender,
                    'weapon': fencer.weapon,
                    'brackets': fencer_brackets,
                    'total_points': fencer_points
                })
            
            # Sort fencers by points (descending)
            fencers_data.sort(key=lambda x: x['total_points'], reverse=True)
            
            # Add statistics to club data
            club_data['members'] = fencers_data
            club_data['total_points'] = total_points
            club_data['weapon_distribution'] = weapon_counts
            club_data['bracket_distribution'] = bracket_counts
            
            return jsonify(club_data), 200
    except Exception as e:
        logger.error(f"Error getting club {club_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/clubs/<string:club_id>/cumulative-points', methods=['GET'])
def get_club_cumulative_points(club_id):
    """Get cumulative points over time for a club"""
    try:
        with get_session_context() as db:
            club = db.query(Club).filter_by(club_id=club_id).first()
            
            if not club:
                return jsonify({'error': 'Club not found'}), 404
            
            # Get all tournament results for this club's fencers, ordered by date
            from sqlalchemy import func
            
            results = db.query(
                Tournament.date,
                Tournament.tournament_name,
                func.sum(TournamentResult.points_awarded).label('points')
            ).select_from(TournamentResult).join(
                Tournament, TournamentResult.tournament_id == Tournament.tournament_id
            ).join(
                Fencer, TournamentResult.fencer_id == Fencer.fencer_id
            ).filter(
                Fencer.club_id == club_id,
                Tournament.status == 'Completed'
            ).group_by(
                Tournament.date,
                Tournament.tournament_name,
                Tournament.tournament_id
            ).order_by(
                Tournament.date
            ).all()
            
            # Calculate cumulative points
            cumulative_data = []
            cumulative_total = 0
            
            for result in results:
                cumulative_total += result.points
                cumulative_data.append({
                    'date': result.date.strftime('%Y-%m-%d') if result.date else None,
                    'tournament_name': result.tournament_name,
                    'points_earned': int(result.points),
                    'cumulative_points': cumulative_total
                })
            
            return jsonify(cumulative_data), 200
    except Exception as e:
        logger.error(f"Error getting cumulative points for club {club_id}: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SEASON ENDPOINTS
# ============================================================================

@app.route('/api/seasons', methods=['GET'])
def get_seasons():
    """Get all seasons"""
    try:
        with get_session_context() as db:
            seasons = db.query(Season).order_by(Season.start_date.desc()).all()
            return jsonify([s.to_dict() for s in seasons]), 200
    except Exception as e:
        logger.error(f"Error getting seasons: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/seasons', methods=['POST'])
def create_season():
    """Create a new season (dev tool - no auth required)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('start_date') or not data.get('end_date'):
            return jsonify({'error': 'Missing required fields: name, start_date, end_date'}), 400
        
        with get_session_context() as db:
            # Check if season name already exists
            existing = db.query(Season).filter_by(name=data['name']).first()
            if existing:
                return jsonify({'error': f'Season "{data["name"]}" already exists. Please use a different name or delete the existing season first.'}), 409
            
            season = Season(
                name=data['name'],
                start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
                end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
                status=data.get('status', 'Upcoming'),
                description=data.get('description')
            )
            
            db.add(season)
            db.commit()
            db.refresh(season)
            
            logger.info(f"Created season: {season.name}")
            return jsonify(season.to_dict()), 201
            
    except Exception as e:
        logger.error(f"Error creating season: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/seasons/<int:season_id>', methods=['GET'])
def get_season_by_id(season_id):
    """Get season details"""
    try:
        with get_session_context() as db:
            season = db.query(Season).filter_by(season_id=season_id).first()
            
            if not season:
                return jsonify({'error': 'Season not found'}), 404
            
            return jsonify(season.to_dict()), 200
    except Exception as e:
        logger.error(f"Error getting season {season_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/seasons/<int:season_id>', methods=['DELETE'])
def delete_season(season_id):
    """Delete a season and optionally its tournaments (dev tool - no auth required)"""
    try:
        with get_session_context() as db:
            season = db.query(Season).filter_by(season_id=season_id).first()
            
            if not season:
                return jsonify({'error': 'Season not found'}), 404
            
            season_name = season.name
            tournament_count = len(season.tournaments)
            
            # Delete the season (tournaments will have season_id set to NULL due to ondelete='SET NULL')
            db.delete(season)
            db.commit()
            
            logger.info(f"Deleted season {season_name} (ID: {season_id}). {tournament_count} tournaments were unlinked.")
            return jsonify({
                'message': f'Season "{season_name}" deleted successfully',
                'tournaments_unlinked': tournament_count
            }), 200
            
    except Exception as e:
        logger.error(f"Error deleting season {season_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/seasons/<int:season_id>/simulate', methods=['POST'])
def simulate_season(season_id):
    """
    Simulate a full season with tournaments and results (dev tool - no auth required).
    
    Request body:
        - num_tournaments: Number of tournaments to generate (default: 100)
        - reset_rankings: Whether to reset rankings before simulation (default: true)
    """
    try:
        data = request.get_json() or {}
        num_tournaments = data.get('num_tournaments', 100)
        reset_rankings = data.get('reset_rankings', True)
        
        with get_session_context() as db:
            season = db.query(Season).filter_by(season_id=season_id).first()
            
            if not season:
                return jsonify({'error': 'Season not found'}), 404
            
            # Run simulation
            stats = simulate_full_season(
                session=db,
                season_name=season.name,
                start_date=season.start_date,
                end_date=season.end_date,
                num_tournaments=num_tournaments,
                reset_rankings=reset_rankings
            )
            
            logger.info(f"Simulated season {season.name}: {stats['total_results']} results created")
            return jsonify({
                'message': 'Season simulation completed successfully',
                'statistics': stats
            }), 200
            
    except Exception as e:
        logger.error(f"Error simulating season {season_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rankings/reset', methods=['POST'])
def reset_all_rankings():
    """
    Reset all fencer rankings to zero (dev tool - no auth required).
    This will set points and tournaments_attended to 0 for all rankings,
    delete all tournament results, and delete all tournaments.
    """
    try:
        with get_session_context() as db:
            # Reset rankings
            rankings = db.query(Ranking).all()
            rankings_count = len(rankings)
            
            for ranking in rankings:
                ranking.points = 0
                ranking.tournaments_attended = 0
                ranking.rank = None
            
            # Delete all tournament results
            results = db.query(TournamentResult).all()
            results_count = len(results)
            for result in results:
                db.delete(result)
            
            # Delete all tournaments
            tournaments = db.query(Tournament).all()
            tournaments_count = len(tournaments)
            for tournament in tournaments:
                db.delete(tournament)
            
            db.commit()
            
            logger.info(f"Reset {rankings_count} rankings, deleted {results_count} tournament results, and deleted {tournaments_count} tournaments")
            return jsonify({
                'message': 'All rankings, tournament results, and tournaments reset successfully',
                'rankings_reset': rankings_count,
                'results_deleted': results_count,
                'tournaments_deleted': tournaments_count
            }), 200
            
    except Exception as e:
        logger.error(f"Error resetting rankings: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'AllFence API is running'}), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Get port and debug mode from environment
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AllFence API server on port {port} (debug={debug})...")
    app.run(debug=debug, host='0.0.0.0', port=port)
