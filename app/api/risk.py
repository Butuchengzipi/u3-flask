# coding=utf-8

"""
API  risk data  return  risk table


"""
from flask import url_for, jsonify, request
from . import api
from ..models import db, Info, RiskData

baseDir = r'D:\\Performance'


@api.route('/risk/')
def get_risk():
    """
    查询 本周风险
    :return: jsonify
    """
    page = request.args.get('page', 1, type=int)
    pagination = RiskData.query.order_by(RiskData.id.desc()).paginate(
                                                                page,
                                                                per_page=1,
                                                                error_out=False)  # 变量只能用大写字母
    risks = pagination.items

    prev = None
    next = None

    if pagination.has_prev:
        prev = url_for('api.get_risk', page=page-1)
    if pagination.has_next:
        next = url_for('api.get_risk', page=page+1)

    mix = {}

    for item in risks:
        print(item.info_id)
        risk_info = Info.query.filter_by(id=item.info_id).first()
        print(risk_info.id, risk_info.date, risk_info.test_content, risk_info.remark)
        date = risk_info.date

        risk_info_all = Info.query.filter_by(date=date).all()

        for items in risk_info_all:
            mix[items.test_content] = items.remark                      # 测试内容及其 备注 ，塞入到 字典里

        return jsonify({
            'risk': [risk.to_json() for risk in risks],
            'pre_url': prev,
            'next_url': next,
            'page': page,
            'count': pagination.total,
            'date': date,
            'mix': mix
        })


@api.route('/commit_risk', methods=['POST'])
def post_commit_risk():
    """
    提交风险信息
    :return: 状态值，供前端捕获
    """
    data = request.get_json(silent=True)

    for items in data.values():
        date = list(items.values())[0]  # 这里需要转换成 list类型，具体原因， py2 和 py3 的写法不同
        project = list(items.values())[1]
        branch = list(items.values())[2]
        this_weekly = list(items.values())[3]
        last_weekly_repair = list(items.values())[4]
        conclusion = list(items.values())[5]

        print(date, project, branch, this_weekly, last_weekly_repair, conclusion)

        info = Info.query.filter_by(date=date,
                                    project=project,
                                    branch=branch).first()

        if info is None:
            return 'NotFound'
        elif RiskData.query.filter_by(info_id=info.id).first() is not None:
            print('Have commited...', info.id)
            return 'Have'
        else:
            try:
                risk = RiskData(this_weekly=this_weekly,
                                last_weekly_repair=last_weekly_repair,
                                conclusion=conclusion,
                                info_id=info.id)
                db.session.add(risk)
                db.session.commit()
                return 'True'
            except Exception as e:
                db.session.rollback()
                return e


@api.route('/search_risk')
def search_risk():
    risk = RiskData.query.all()

    info_date = []
    for item in risk:
        info = Info.query.filter_by(id=item.info_id).first()
        if info.date not in info_date:                                  # 向前端回传 date
            info_date.append(info.date)
    print(info_date)
    return jsonify({
        'info_date': info_date
    })
