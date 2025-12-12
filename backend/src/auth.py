"""
Authentication utilities for JWT token management
"""
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict

# Secret key for JWT - in production, use environment variable
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
ALGORITHM = 'HS256'
TOKEN_EXPIRATION_HOURS = 24


def generate_token(user_id: int, username: str, is_admin: bool) -> str:
    """
    Generate JWT token for authenticated user
    
    Args:
        user_id: User's database ID
        username: User's username
        is_admin: Whether user has admin privileges
    
    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict]:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload dictionary if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_header() -> Optional[str]:
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


def require_auth(f):
    """
    Decorator to require authentication for route
    Adds user_data to kwargs
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        user_data = decode_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        kwargs['user_data'] = user_data
        return f(*args, **kwargs)
    
    return decorated


def require_admin(f):
    """
    Decorator to require admin privileges
    Adds user_data to kwargs
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        user_data = decode_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if not user_data.get('is_admin'):
            return jsonify({'error': 'Admin privileges required'}), 403
        
        kwargs['user_data'] = user_data
        return f(*args, **kwargs)
    
    return decorated
