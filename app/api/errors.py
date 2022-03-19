# coding=utf-8
"""
APi error
"""
from flask import jsonify
from app.exceptions import ValidationError
from . import api


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})  # 禁止访问
    response.status_code = 400  # response 状态码 400
    return response


def forbidden(message):  # 禁止访问
    response = jsonify({'error': 'forbidden', 'message': message})  # 禁止访问
    response.status_code = 403  # response 状态码 403
    return response


def unauthorized(message):  # 未授权
    response = jsonify({'error': 'unauthorized', 'message': message})  # 未授权
    response.status_code = 401  # response 状态码 401
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
