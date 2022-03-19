# coding=utf-8

"""
config file
配置文件里，避免写入密码

仅使用大写字母重命名配置变量!!!

变量只能用大写字母!!!

"""

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """ base config """
    FLASK_APP = os.environ.get('FLASK_APP') or 'chengzi.py'
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG') or '1'
    FLASK_ENV = 'development'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Something'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.163.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'wi180612@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'FPZXYIASFPXYQECB'  # 这里不是邮箱密码，是授权码

    CHENGZIPI_MAIL_SUBJECT_PREFIX = '[Chengzipi]'  # 仅使用大写字母重命名配置变量!!!
    CHENGZIPI_MAIL_SENDER = 'Chengzipi Admin <wi180612@163.com>'  # 仅使用大写字母重命名配置变量!!!
    CHENGZIPI_ADMIN = os.environ.get('Chengzipi_ADMIN')  # 仅使用大写字母重命名配置变量!!!
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CHENGZIPI_POSTS_PER_PAGE = 9  # 仅使用大写字母重命名配置变量!!!

    SQLALCHEMY_RECORD_QUERIES = True    # 启用记录查询统计数据的功能
    CHENGZIPI_SLOW_DB_QUERY_TIME = 0.5  # 设置缓慢查询的阈（yu）值为0.5s

    VUE_SECRET_KEY = 'TianSeJiangWan,QiuXinRuGua'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # 出错时邮件通知管理员
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_SSL', None):
                secure = ()

        mail_handler = SMTPHandler(mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                                   fromaddr=cls.CHENGZIPI_MAIL_SENDER,
                                   toaddrs=[cls.CHENGZIPI_ADMIN],
                                   subject=cls.CHENGZIPI_MAIL_SUBJECT_PREFIX + 'Application Error',
                                   credentials=credentials,
                                   secure=secure)
        mail_handler.setLevel(logging.ERROR)    # 日志等级 ERROR，只有发生严重错误时才会发送电子邮件
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig

}
