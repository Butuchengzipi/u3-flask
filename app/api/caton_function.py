# coding=utf-8
"""
API caton - function

有一处  date  需要改掉

"""
from flask import url_for, jsonify, request, current_app
from . import api
from ..models import ProfileData, Info

import os


@api.route('/caton_function', methods=['POST'])
def get_caton_function():
    data = request.get_json(silent=True)

    page = request.args.get('page', 1, type=int)

    print(data)
    for items in data.values():
        print('************', items.values(), type(items.values()))
        # date = list(items.values())[0][:10].replace('-', '.')  # 这里需要转换成 list类型，具体原因， py2 和 py3 的写法不同
        # print(date[0:10], date[:10], date[:10].replace('-', '.'))
        date = list(items.values())[0]  # 这里需要转换成 list类型，具体原因， py2 和 py3 的写法不同

        project = list(items.values())[1]
        branch = list(items.values())[2]
        model = list(items.values())[3]
        frame = list(items.values())[4]
        test_content = list(items.values())[5]

        print(type(date), len(date), date)
        print(date, project, branch, model, frame, test_content)

        print(Info.query.filter_by(date=date,    # 区分 6.11 和 06.11
                                   project=project,
                                   branch=branch,
                                   model=model,
                                   frame=frame,
                                   test_content=test_content).first_or_404().remark)

        info_id = Info.query.filter_by(date=date,    # 这里要改掉
                                       project=project,
                                       branch=branch,
                                       model=model,
                                       frame=frame,
                                       test_content=test_content).first_or_404().id

        # info_id = '1'
        pagination = ProfileData.query.filter_by(info_id=info_id).paginate(page,
                                                                           per_page=current_app.config['CHENGZIPI_POSTS_PER_PAGE'],
                                                                           error_out=False)  # 变量只能用大写字母
        caton_function = pagination.items
        prev = None
        next = None

        if pagination.has_prev:
            prev = url_for('api.get_caton_function', page=page - 1)
        if pagination.has_next:
            next = url_for('api.get_caton_function', page=page + 1)

        return jsonify({
            'caton_function': [function.to_json() for function in caton_function],
            'pre_url': prev,
            'next_url': next,
            'count': pagination.total
        })


@api.route('/transmission', methods=['POST'])
def get_transmission():
    """
    # 用于返回文件流, 后调整为返回 file.read()
    :param :
    :return:
    """
    data = request.get_json(silent=True)
    print(data, data.values())

    for items in data.values():
        print(items, type(items))
        filePath = list(data.values())[0]  # 这里不太对， 与上面的 caton_function 里的 dict 套 dict 不一样
        profileFilename = list(data.values())[1]

        os.chdir(filePath)
        file = open(profileFilename, 'r')   # mode='r' encoding='cp936'
        svg_content = file.read()
        # print(type(file), file.read())

        # file2 = open(profileFilename, 'rb')
        # base64_svg = base64.b64encode(file2.read())
        file.close()
        return svg_content


@api.route('/search_profile_date')
def search_profile_date():
    profile_date = ProfileData.query.all()

    info_date = []
    for item in profile_date:
        info = Info.query.filter_by(id=item.info_id).first()
        if info.date not in info_date:                                  # 向前端回传 date
            info_date.append(info.date)

    return jsonify({
        'info_date': info_date
    })


@api.route('/date_change', methods=['POST'])
def date_change():
    data = request.get_json(silent=True)

    print(data)
    for items in data.values():
        date = items  # 这里需要转换成 list类型，具体原因， py2 和 py3 的写法不同

        info = Info.query.filter_by(date=date).all()
        info_project = []
        info_branch = []
        info_model = []
        info_frame = []
        info_test_content = []

        for item in info:
            if item.project not in info_project:                            # 向前端回传 project
                info_project.append(item.project)
            if item.branch not in info_branch:                              # 向前端回传 branch
                info_branch.append(item.branch)
            if item.model not in info_model:                                # 向前端回传 model
                info_model.append(item.model)
            if item.frame not in info_frame:                                # 向前端回传 frame
                info_frame.append(item.frame)
            if item.test_content not in info_test_content:                  # 向前端回传 test_content
                info_test_content.append(item.test_content)

        return jsonify({
            'Info': [item.to_json() for item in info],
            'info_project': info_project,
            'info_branch': info_branch,
            'info_model': info_model,
            'info_frame': info_frame,
            'info_test_content': info_test_content
        })
