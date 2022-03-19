# coding=utf-8
"""
API __init__
"""

from flask import Blueprint

api = Blueprint('api', __name__)

from . import decorators, errors, posts, users, caton_function, profile_archive, perfdog_data, risk, secret_key, generate_report
"""  这里不能用 * 代替 导入项"""
