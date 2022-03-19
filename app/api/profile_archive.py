# coding=utf-8

"""
API profile - archive  提供下载

有一处  date  需要改掉

"""
from flask import url_for, jsonify, request, current_app
from . import api, tools
from ..models import Info, ProfileData

import os

baseDir = r'D:\\Performance'                                                        # 操作目录


@api.route('/archive/')
def get_profile_archive():
    """
    查询当前 存在的 profile 信息
    :return: jsonify
    """
    info_id = ProfileData.query.order_by(ProfileData.info_id.desc()).first().info_id
    this_week = Info.query.filter_by(id=info_id).first()                       # 查询最新数据

    print(type(Info.query.order_by(Info.date.desc()).first()), this_week.date, this_week.id)

    page = request.args.get('page', 1, type=int)
    pagination = Info.query.order_by(Info.date.desc()).group_by(Info.date).paginate(
                                                                page,
                                                                per_page=current_app.config['CHENGZIPI_POSTS_PER_PAGE'],
                                                                error_out=False)  # 变量只能用大写字母
    archive = pagination.items

    prev = None
    next = None

    if pagination.has_prev:
        prev = url_for('api.get_profile_archive', page=page-1)
    if pagination.has_next:
        next = url_for('api.get_profile_archive', page=page+1)

    return jsonify({
        'archive': [rar.to_json() for rar in archive],
        'pre_url': prev,
        'next_url': next,
        'page': page,
        'count': pagination.total,
        'this_week': [this_week.to_json()]      # 这里不能直接返回 .to_json() 需要套上 dict
    })


@api.route('/transmission_rar', methods=['POST'])
def get_transmission_rar():
    """
    用于返回文件流, 后调整为返回 file.read()
    :return: 文件流，以下载
    """
    data = request.get_json(silent=True)

    date = list(data.values())[0]  # 这里不太对， 与上面的 caton_function 里的 dict 套 dict 不一样

    info_id = Info.query.filter_by(date=date).first().id
    if ProfileData.query.filter_by(info_id=info_id).first() is not None:
        filePath = os.path.join(baseDir, date)

        profileFilename = date + '.zip'

        os.chdir(filePath)

        read_hey = open(profileFilename, 'rb')      # mode='r' encoding='cp936'
        rar_content = read_hey.read()

        read_hey.close()
        return rar_content
    else:
        return 'only perfdog data'


@api.route('/commit_profile', methods=['POST'])
def post_commit_profile():
    """
    接收 profile 信息, 存入数据库
    :return: 状态值，供前端捕获
    """
    data = request.get_json(silent=True)
    print(data, type(data))

    for items in data.values():
        # print(items, type(items), len(items))
        date = list(items.values())[0]  # 这里需要转换成 list类型，具体原因， py2 和 py3 的写法不同
        project = list(items.values())[1]
        branch = list(items.values())[2]
        model = list(items.values())[3]
        frame = list(items.values())[4]
        test_content = list(items.values())[5]
        remark = list(items.values())[6]
        secret_key = list(items.values())[7]
        print(date, project, branch, model, frame, test_content, remark, secret_key)
        # # 生成目录，返回路径

        try:
            savePath, high_path = tools.dirOperations(date, project, branch, model, test_content, frame)    # 生成相关的目录

            tools.copy_debug_output(savePath)                   # 复制 debug_output 进创建的目录下
            tools.unzip_file(savePath)                          # 解压上传的rar文件
            tools.copy_analysisFile(savePath)                   # 复制所需运行的脚本文件

            tools.analyse_excel(date, project, branch, model, test_content, frame, remark,
                                high_path)                      # 这里的 csv文件，实际应该是 txt ，可能是生成的时候改了文件类型
            return 'True'
        except Exception as e:
            return e


@api.route('/receive_profile', methods=['POST'])
def receive_profile():
    """
    存入 前端传来的文件
    :return: 随便return
    """
    # req = request
    # print(req, req.files)        # 这里传了一个空的 ImmutableMultiDict([])

    debug_output = request.files['file']

    file_name = debug_output.filename or 'debug_output.rar'
    destination = '/'.join([baseDir, file_name])
    debug_output.save(destination)
    print(type(debug_output), 'Ok !')
    return 'debug_output has been saved'


@api.route('/compressed_file', methods=['POST'])
def post_compressed_file():
    """ 压缩 profile 文件夹 """
    data = request.get_json(silent=True)
    print(data, type(data))

    for item in data.values():
        date = item
        print(date)
        if Info.query.filter_by(date=date).first():
            if tools.cre_tarfile(date):  # 打包文件
                return 'True'
            else:
                return 'Error'
        else:
            return 'NotFound'
