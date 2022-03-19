# coding=utf-8
"""
API posts
"""
from flask import g, url_for, jsonify, request, current_app
from . import api
from .decorators import Permission_required
from .errors import forbidden
from ..models import db, Post, Permission


@api.route('/posts')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(page, per_page=current_app.config['CHENGZIPI_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    next = None

    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1)
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1)

    return jsonify({
        'posts': [post.to_json()for post in posts],
        'pre_url': prev,
        'next_url': next,
        'page': page,
        'count': pagination.total
    })


@api.route('/posts/<int:id>')   # 返回一篇博客文章
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/', methods=['POST'])   # 创建一篇博客文章
@Permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id=post.id)}


@api.route('/posts/<int:id>', methods=['POST'])   # 修改一篇博客文章
@Permission_required(Permission.WRITE)
def edit_post():
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.COMMIT):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())


@api.route('/create_post', methods=['POST'])   # 创建一篇博客文章
def create_post():
    data = request.get_json(silent=True)
    print(data, type(data))

    for items in data.values():
        body = items
        if body is None:
            return 'ID Error'
        post = Post(body=body,
                    author_id=1)
        print(post)
        db.session.add(post)
        db.session.commit()
        return 'True'
