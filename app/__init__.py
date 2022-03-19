# coding:utf-8
from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__, static_folder="../static")
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    # 添加内容...

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint,  url_prefix='/api/v1')  # 注册 api 蓝本

    return app
