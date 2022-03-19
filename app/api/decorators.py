# coding=utf-8
"""
装饰器
"""
from functools import wraps
from flask import g
from .errors import forbidden


# Permission_required 装饰器
def Permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
