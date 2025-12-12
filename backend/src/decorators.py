"""
Session Management Decorator

This module provides decorators to automatically handle database sessions
and reduce code duplication across the application.
"""

from functools import wraps
from typing import Callable, Any
from .database import get_session_context
import logging

logger = logging.getLogger(__name__)


def with_session(func: Callable) -> Callable:
    """
    Decorator to automatically manage database sessions.
    
    This decorator reduces code duplication by handling session creation,
    error handling, and cleanup automatically. If the function receives
    a session parameter, it uses that. Otherwise, it creates a new session.
    
    Usage:
        @with_session
        def my_function(param1: str, param2: int, session=None):
            # Use session directly
            user = session.query(User).first()
            return user
        
        # Call without session - decorator creates one
        result = my_function("value", 42)
        
        # Call with session - decorator uses provided one
        with get_session_context() as sess:
            result = my_function("value", 42, session=sess)
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function that handles sessions
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if session is provided as keyword argument
        session = kwargs.get('session')
        
        # If no session provided, create one using context manager
        if session is None:
            with get_session_context() as new_session:
                kwargs['session'] = new_session
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {e}")
                    raise
        else:
            # Session was provided, just call the function
            return func(*args, **kwargs)
    
    return wrapper


def batch_operation(func: Callable) -> Callable:
    """
    Decorator for batch database operations.
    
    Similar to @with_session but optimized for operations that should
    be committed as a batch at the end.
    
    Usage:
        @batch_operation
        def process_many_items(items: List[Item], session=None):
            for item in items:
                # Do something with item
                session.add(item)
            # session.commit() is called automatically after
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function with batch commit handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = kwargs.get('session')
        
        if session is None:
            with get_session_context() as new_session:
                kwargs['session'] = new_session
                try:
                    result = func(*args, **kwargs)
                    new_session.commit()
                    return result
                except Exception as e:
                    new_session.rollback()
                    logger.error(f"Batch operation failed in {func.__name__}: {e}")
                    raise
        else:
            return func(*args, **kwargs)
    
    return wrapper


def transactional(func: Callable) -> Callable:
    """
    Decorator for transactional database operations.
    
    Ensures the operation either fully succeeds or fully fails.
    Useful for complex multi-step operations.
    
    Usage:
        @transactional
        def transfer_points(from_fencer_id: int, to_fencer_id: int, points: int, session=None):
            from_fencer = session.query(Fencer).get(from_fencer_id)
            to_fencer = session.query(Fencer).get(to_fencer_id)
            
            from_fencer.points -= points
            to_fencer.points += points
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function with transaction handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = kwargs.get('session')
        
        if session is None:
            with get_session_context() as new_session:
                kwargs['session'] = new_session
                try:
                    result = func(*args, **kwargs)
                    new_session.commit()
                    logger.info(f"Transaction {func.__name__} committed successfully")
                    return result
                except Exception as e:
                    new_session.rollback()
                    logger.error(f"Transaction {func.__name__} rolled back: {e}")
                    raise
        else:
            return func(*args, **kwargs)
    
    return wrapper
