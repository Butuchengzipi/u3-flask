# coding=utf-8
"""
API perfdog - data          有一处  date  需要改掉

1.查询 perfdog 数据

2.提交 perfdog 数据

3.修改
4.删除

"""
from flask import jsonify, request
from . import api
from ..models import db, Info, PerfdogData

baseDir = r'D:\\Performance'


@api.route('/perfdog_data/', methods=['POST'])
def get_perfdog_data():
    """
    查询 perfdog 数据
    :return: jsonify
    """
    data = request.get_json(silent=True)

    typeof = ''
    search_data = ''

    for items in data.values():
        print('*********items ***********', items)
        print('*********items.values() ***********', items.values())

        if items is '':
            print('type is None !!!')
            return 'None'

        typeof_data = list(items.values())[0]
        for key, value in typeof_data.items():
            print(key, value)
            if len(value) != 0:  # 判断长度是否为 0
                typeof = key
                search_data = value
                print('**********typeof**********', typeof, '**********search_data**********', search_data)

    if typeof == 'date':
        info_id = Info.query.filter_by(date=search_data).order_by(Info.date.desc()).all()
    elif typeof == 'project':
        info_id = Info.query.filter_by(project=search_data).order_by(Info.date.desc()).all()
    elif typeof == 'branch':
        info_id = Info.query.filter_by(branch=search_data).order_by(Info.date.desc()).all()
    elif typeof == 'model':
        info_id = Info.query.filter_by(model=search_data).order_by(Info.date.desc()).all()
    elif typeof == 'frame':
        info_id = Info.query.filter_by(frame=search_data).order_by(Info.date.desc()).all()
    elif typeof == 'test_content':
        info_id = Info.query.filter_by(test_content=search_data).order_by(Info.date.desc()).first_or_404()
    else:
        return Info.query.order_by(Info.date.desc()).filter_by(test_content=search_data).first_or_404()
    # print(info_id, type(info_id))

    return_list = []

    for item in info_id:
        # print('***item***', item, item.id)
        perfdog_data = PerfdogData.query.filter_by(info_id=item.id).order_by(PerfdogData.info_id.desc()).first()
        if perfdog_data is not None:
            print('*** perfdog_data ***', type(perfdog_data), perfdog_data, perfdog_data.id)
            return_data = {
                'id': item.id,
                'date': item.date,
                'project': item.project,
                'branch': item.branch,
                'model': item.model,
                'test_content': item.test_content,
                'frame': item.frame,
                'remark': item.remark,
                'avgFPS': perfdog_data.avgFPS,
                'varFPS': perfdog_data.varFPS,
                'dropFPS': perfdog_data.dropFPS,
                'jank': perfdog_data.jank,
                'bigJank': perfdog_data.bigJank,
                'avgMemory': perfdog_data.avgMemory,
                'avgCPU': perfdog_data.avgCPU,
                'link': perfdog_data.link,
                'password': perfdog_data.password,
            }
            return_list.append(return_data)
            # print('***** return_data *****', return_data)
            # print('***** return_list *****', return_list)
    return jsonify({
        'perfdog_data': [item for item in return_list]
    })


@api.route('/commit_perfdog', methods=['POST'])
def post_commit_perfdog():
    """
    提交 perfdog 数据
    :return: 状态值，供前端捕获
    """
    data = request.get_json(silent=True)
    print(data, type(data))

    for items in data.values():
        date = list(items.values())[0]  # 这里需要转换成 list类型，具体原因， py2 和 py3 的写法不同
        project = list(items.values())[1]
        branch = list(items.values())[2]
        model = list(items.values())[3]
        frame = list(items.values())[4]
        test_content = list(items.values())[5]
        remark = list(items.values())[6]
        secret_key = list(items.values())[7]
        avgFPS = list(items.values())[8]
        varFPS = list(items.values())[9]
        dropFPS = list(items.values())[10]
        jank = list(items.values())[11]
        bigJank = list(items.values())[12]
        avgMemory = list(items.values())[13]
        avgCPU = list(items.values())[14]
        link = list(items.values())[15].split('Password:')[0]
        password = list(items.values())[15].split('Password:')[1]

        print(secret_key)
        # print(date, project, branch, model, frame, test_content, remark, secret_key)
        # print(avgFPS, varFPS, dropFPS, jank, bigJank, avgMemory, avgCPU, link, password)

        info = Info.query.filter_by(date=date, project=project, branch=branch, model=model, frame=frame,
                                       test_content=test_content, remark=remark).first()

        if info is None:
            """ 若无 info.id , 新增一个 """
            create_info = Info(date=date, project=project, branch=branch, model=model, frame=frame,
                             test_content=test_content, remark=remark)
            db.session.add(create_info)
            db.session.commit()

            info = Info.query.filter_by(date=date,
                                           project=project,
                                           branch=branch,
                                           model=model,
                                           frame=frame,
                                           test_content=test_content,
                                           remark=remark).first()

        if PerfdogData.query.filter_by(info_id=info.id).first() is not None:
            print('Have commited...')
            return 'Have'
        else:
            perfdog = PerfdogData(avgFPS=avgFPS,
                                  varFPS=varFPS,
                                  dropFPS=dropFPS,
                                  jank=jank,
                                  bigJank=bigJank,
                                  avgMemory=avgMemory,
                                  avgCPU=avgCPU,
                                  link=link,
                                  password=password,
                                  info_id=info.id)
            try:
                print('******** commit **********')
                db.session.add(perfdog)
                db.session.commit()
                return 'True'
            except Exception as e:
                db.session.rollback()
                return e


@api.route('/change_perfdog', methods=['POST'])
def post_change_perfdog():
    """
    修改 perfdog 数据
    :return: 状态值，供前端捕获
    """
    data = request.get_json(silent=True)
    print(data, type(data))

    for items in data.values():
        print(list(items.values()))
        id = list(items.values())[0]
        date = list(items.values())[1]  # 这里需要转换成 list类型，具体原因， py2 和 py3 的写法不同
        project = list(items.values())[2]
        branch = list(items.values())[3]
        model = list(items.values())[4]
        frame = list(items.values())[5]
        test_content = list(items.values())[6]
        remark = list(items.values())[7]
        secret_key = list(items.values())[8]
        avgFPS = list(items.values())[9]
        varFPS = list(items.values())[10]
        dropFPS = list(items.values())[11]
        jank = list(items.values())[12]
        bigJank = list(items.values())[13]
        avgMemory = list(items.values())[14]
        avgCPU = list(items.values())[15]
        link = list(items.values())[16].split('Password:')[0]
        password = list(items.values())[16].split('Password:')[1]

        print(secret_key)

        if id is None:
            return 'ID Error'

        info = Info.query.filter_by(id=id).first()                                 # 先查询出结果
        info.date = date
        info.project = project
        info.branch = branch
        info.model = model
        info.test_content = test_content
        info.frame = frame
        info.remark = remark

        perfdog = PerfdogData.query.filter_by(info_id=id).first()                   # 先查询出结果
        perfdog.avgFPS = avgFPS
        perfdog.varFPS = varFPS
        perfdog.dropFPS = dropFPS
        perfdog.jank = jank
        perfdog.bigJank = bigJank
        perfdog.avgMemory = avgMemory
        perfdog.avgCPU = avgCPU
        perfdog.link = link
        perfdog.password = password

        try:
            print('******** commit **********')
            db.session.commit()                                                     # 直接提交 即可，不需要add
            return 'True'
        except Exception as e:
            return str(e)


@api.route('/delete_perfdog', methods=['POST'])
def post_delete_perfdog():
    """
    删除 perfdog 数据
    :return: 状态值，供前端捕获
    """
    data = request.get_json(silent=True)
    print(data, type(data))

    for items in data.values():
        # print(list(items.values()))
        # id = list(items.values())[0]
        print(items, type(items))
        id = items
        if id is None:
            return 'ID Error'

        info = Info.query.filter_by(id=id).first()                                 # 先查询出结果
        perfdog = PerfdogData.query.filter_by(info_id=id).first()                   # 先查询出结果
        # db.session.delete(info)
        # db.session.delete(perfdog)
        print(info, perfdog)
        try:
            print('******** delete **********')
            # db.session.commit()                                                     # 直接提交 即可，不需要add
            return 'True'
        except Exception as e:
            return str(e)


@api.route('/search_perfdog_date')
def search_perfdog_date():
    perfdog_date = PerfdogData.query.all()

    info_date = []
    for item in perfdog_date:
        info = Info.query.filter_by(id=item.info_id).first()
        if info.date not in info_date:                                  # 向前端回传 date
            info_date.append(info.date)

    return jsonify({
        'info_date': info_date
    })
