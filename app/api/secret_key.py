# coding=utf-8

"""
API 向前端回传  secret_key，用于校验是否有提交权限  上传

"""
from flask import request, current_app
from . import api


@api.route('/secret_key', methods=['POST'])
def get_secret_key():
    """ 用于校验 前端 传来的 文件提交秘钥值是否正确 """
    data = request.get_json(silent=True)

    for item in data.values():
        secret_key = item
        if secret_key != current_app.config['VUE_SECRET_KEY']:
            print(secret_key)
            return 'False'
        else:
            return 'True'
