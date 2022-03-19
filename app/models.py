# coding=utf-8

"""
DATABASE  Models
修改数据库后
flask db migrate -m "initial migration"
flask db upgrade

"""
from werkzeug.security import generate_password_hash, check_password_hash

from flask import url_for, current_app  # 使用 flask 框架默认的 current_app

from . import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.exceptions import ValidationError
import datetime

datetime = datetime.datetime


class Permission:  # 使用 2 的次幂 表示权限，使得任意权限组合的值 都是 "唯一" 的!
    READ = 1
    WRITE = 2
    DOWN = 4
    COMMIT = 8


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)  # 设置索引，提升搜索速度
    permissions = db.Column(db.Integer)  # 权限
    users = db.relationship('User', backref='role', lazy='dynamic')  # lazy -> 禁止自动执行

    def __init__(self, **kwargs):  #
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):  # 增加权限
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):  # 降低权限
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):  # 重置权限
        self.permissions = 0

    def has_permission(self, perm):  # 查询当前权限
        return self.permissions & perm == perm  # 使用 位与 运算符 & 检查组合权限是否包含指定 的单独权限 返回

    @staticmethod  # 在数据库中创建角色
    def insert_roles():
        roles = {
            'User': [Permission.READ, Permission.WRITE, Permission.DOWN],
            'Guest': [Permission.READ, Permission.WRITE],
            'AnonymousUser': [Permission.READ],
            'Administrator': [Permission.READ, Permission.WRITE, Permission.DOWN, Permission.COMMIT]
        }

        default_role = 'User'

        for r in roles:
            role = Role.query.filter_by(name=r).first()  # 查找现有 name 为 r 的 Role对象
            if role is None:  # 当 r 对象 不存在时
                role = Role(name=r)  # 新建对象
            role.reset_permission()  # 重置 权限

            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Post(db.Model):  # 类博客模型
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_json(self):      # 转换成序列化字典
        json_post = {
            'url': url_for('api.get_post', id=self.id),     # 返回对应资源的url
            'body': self.body,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id)    # 返回对应资源的url， 所调用路由需要在 api蓝本中定义
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


class User(db.Model):  # User表
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)  # 设置默认值为False
    name = db.Column(db.String(64))
    # last_seen = db.Column(db.DataTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User %r %r %r>' % (self.username, self.email, self.role_id)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'posts_url': url_for('api.get_user_posts', id=self.id),
        }
        return json_user

    def generate_auth_token(self, expiration):  # 生成一个签名令牌
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)  # 获得令牌
        except Exception as e:
            print(e)
            return None
        return User.query.get(data['id'])  # 返回id

    # def ping(self):  # 实时刷新用户的访问时间
    #     self.last_seen = datetime.datetime.utcnow()
    #     db.session.add(self)
    #     db.session.commit()

    # 赋予用户角色
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is not None:
            if self.email == current_app.config['CHENGZIPI_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, perm):  # 验证用户是否拥有 当前 权限
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):  # 判断管理员权限
        return self.can(Permission.COMMIT)

    @property
    def password(self):  # 当查询用户密码时， 挂起提示
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):  # 密码 盐值处理
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):  # 验证 密码盐值是否正确
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=1800):  # 生成一个令牌，设置过期时间为 1800s
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):  # 检查令牌id 与存储的用户 是否匹配
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))  # 注意 loads() 不是 load()
        except Exception as e:  # 抛出任何error
            print(e)
            return False

        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


class Info(db.Model):                                               # info
    __tablename__ = 'info'
    id = db.Column(db.Integer, primary_key=True)                    # 这里 unique=True 任一一个都不合适
    date = db.Column(db.String(64), index=True)                     # 日期
    project = db.Column(db.String(32), default='U3')                # 项目
    branch = db.Column(db.String(64))                               # 分支，index 设置索引，提升搜索速度
    model = db.Column(db.String(64))                                # 测试机
    test_content = db.Column(db.String(128))                        # 测试内容
    frame = db.Column(db.String(64))                                # 框架
    remark = db.Column(db.String(128))                              # 备注
    perfdogDatas = db.relationship('PerfdogData', backref='info')
    profiledatas = db.relationship('ProfileData', backref='info')
    riskdatas = db.relationship('RiskData', backref='info')

    def to_json(self):      # 转换成序列化字典
        json_function = {
            'date': self.date,     # 返回对应资源的url
            'project': self.project,
            'branch': self.branch,
            'model': self.model,
            'test_content': self.test_content,
            'frame': self.frame,
            'remark': self.remark
        }
        return json_function


class PerfdogData(db.Model):
    __tablename__ = 'perfdogData'
    id = db.Column(db.Integer, primary_key=True)                    # 主键
    avgFPS = db.Column(db.Float)                                    # 平均fps
    varFPS = db.Column(db.Float)                                    # 帧率方差
    dropFPS = db.Column(db.Float)                                   # 降帧次数
    jank = db.Column(db.Float)                                      # 卡顿
    bigJank = db.Column(db.Float)                                   # 严重卡顿
    avgMemory = db.Column(db.Float)                                 # 内存占用
    avgCPU = db.Column(db.Float)                                    # CPU占用
    link = db.Column(db.String(64))                                 # 链接及密码
    password = db.Column(db.String(16))                             # 密码
    info_id = db.Column(db.Integer, db.ForeignKey('info.id'))
        
    def __int__(self, **kwargs):
        pass

    def __repr__(self):
        return '<ProfileData %r>' % self.avgFPS


class ProfileData(db.Model):
    __tablename__ = 'profiledata'
    id = db.Column(db.Integer, primary_key=True)
    function = db.Column(db.String(64))                             # 卡顿函数
    frequency = db.Column(db.Integer)                               # 频率
    delaytime = db.Column(db.Float)                                 # 延迟时间
    totalDelaytime = db.Column(db.Float)                            # 总延迟
    profileFilename = db.Column(db.String(64))                      # svg文件名
    filePath = db.Column(db.String(128))                            # 文件路径
    info_id = db.Column(db.Integer, db.ForeignKey('info.id'))

    def __int__(self, **kwargs):
        pass

    def __repr__(self):
        return '<ProfileData %r>' % self.function

    def to_json(self):      # 转换成序列化字典
        json_function = {
            'function': self.function,     # 返回对应资源的url
            'frequency': self.frequency,
            'delaytime': self.delaytime,
            'totalDelaytime': self.totalDelaytime,
            'profileFilename': self.profileFilename,
            'filePath': self.filePath
        }
        return json_function


class RiskData(db.Model):
    __tablename__ = 'riskdata'
    id = db.Column(db.Integer, primary_key=True)
    this_weekly = db.Column(db.String(256))                 # 本周风险，声明最大长度为 256的字段
    last_weekly_repair = db.Column(db.String(128))          # 上周修复，声明最大长度为 256的字段
    conclusion = db.Column(db.String(256))                  # 结论
    info_id = db.Column(db.Integer, db.ForeignKey('info.id'))

    def __int__(self, **kwargs):
        pass

    def __repr__(self):
        return '<RiskData %r %r %r>' % (self.this_weekly, self.last_weekly_repair, self.conclusion)

    def to_json(self):      # 转换成序列化字典
        json_function = {
            'this_weekly': self.this_weekly,     # 返回对应资源的url
            'last_weekly_repair': self.last_weekly_repair,
            'conclusion': self.conclusion
        }
        return json_function
