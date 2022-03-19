# coding=utf-8

"""
API 根据前端返回的 数据，生成对应日期、项目的 csv文件

以便补充完成每周报告

"""
from flask import request, url_for, jsonify, current_app

from . import api
from ..models import Info, RiskData, PerfdogData

import os
import xlrd
import xlwt
from xlutils.copy import copy

baseDir = r'D:\\Performance'                                                        # 操作目录


@api.route('/generate_csv', methods=['POST'])
def generate_csv():
    """ 用于 生成 csv文件 """
    data = request.get_json(silent=True)

    for items in data.values():
        date = list(items.values())[0]  # 这里需要转换成 list类型，具体原因， py2 和 py3 的写法不同
        project = list(items.values())[1]

        info = Info.query.filter_by(date=date, project=project).first()
        info_all = Info.query.filter_by(date=date, project=project).all()

        os.chdir(os.path.join(baseDir, info.date))

        path = info.date + ' ' + info.project + ' Perfdog 数据对比111.xls'

        """  写入每周风险  """
        risk = RiskData.query.filter_by(info_id=info.id).first()
        risk_this_weekly = risk.this_weekly.split('\\n')
        print(risk_this_weekly)
        risk_last_weekly_repair = risk.last_weekly_repair.split('\\n')

        risk_value = [['本周风险 '],
                      [risk_this_weekly],
                      ['上周修复 '],
                      [risk_last_weekly_repair]]
        write_excel_xls(path, '风险', risk_value)

        """  写入结论 """
        conclusion = [['结论:'], RiskData.query.filter_by(info_id=info.id).first().conclusion.split('\\n')]
        write_excel_xls2(path, '结论', conclusion)

        """  依次写入 sheet  """
        link = []
        for item in info_all:
            perfdog = PerfdogData.query.filter_by(info_id=item.id).first()
            sheet_name = item.test_content

            perfdog_value = [[item.test_content],
                             ['本周数值'],
                             ['', 'AvgFPS',	'VarFPS', 'DropFPS(/h)', 'Jank(/10min)', 'BigJank(/10min)', 'Avg(Memory)[MB]', 'Avg(AppCPU)[%]'],
                             [item.frame, perfdog.avgFPS, perfdog.varFPS,
                              perfdog.dropFPS, perfdog.jank,
                              perfdog.bigJank, perfdog.avgMemory, perfdog.avgCPU],
                             ['相关链接:', perfdog.link],
                             ['Password:', perfdog.password]]

            write_excel_xls2(path, sheet_name, perfdog_value)
            link_all = [str(item.date + ' ' +
                        item.project + ' ' +
                        item.branch + ' ' +
                        item.frame + ' ' +
                        item.test_content + ' ' +
                        '相关链接: ' + perfdog.link + ' Password: ' + perfdog.password)]

            link.append(link_all)
            print(link_all)
        print(link)
        """  写入相关链接 """
        write_excel_xls2(path, '相关链接', link)

        return 'True'


def write_excel_xls(path, sheet_name, value):
    """ 新增 .xls文件 """
    workbook = xlwt.Workbook()  # 新建一个工作簿
    sheet = workbook.add_sheet(sheet_name, cell_overwrite_ok=True)  # 在工作簿中新建一个表格

    font = xlwt.Font()
    font.name = 'name Times New Roman'
    font.height = 20 * 14
    for i in range(0, 9):
        sheet.col(i).width = 11 * 498
    for j in range(0, 128):
        col = sheet.col(j)
        tall_style = xlwt.easyxf('font:height 298;')
        col.set_style(tall_style)

    style0 = xlwt.XFStyle()
    style0.font = font

    font.num_format_str = '#,##0.00'

    index = len(value)  # 获取需要写入数据的行数
    for i in range(0, index):
        for j in range(0, len(value[i])):
            sheet.write(i, j, value[i][j], style0)  # 像表格中写入数据（对应的行和列）
    workbook.save(path)  # 保存工作簿
    print("xls格式表格写入数据成功！")


def write_excel_xls2(path, sheet_name, value):
    """ 复写 xls 文件 """
    wb = xlrd.open_workbook(path, formatting_info=True)

    newb = copy(wb)         # 复制旧表

    sheet = newb.add_sheet(sheet_name, cell_overwrite_ok=True)
    # 如果出现报错：Exception: Attempt to overwrite cell: sheetname='sheet1' rowx=0 colx=0
    # 需要加上：cell_overwrite_ok=True)
    # 这是因为重复操作一个单元格导致的

    # 为样式创建字体
    font = xlwt.Font()
    # 字体类型
    font.name = 'name Times New Roman'
    # 字体大小，11为字号，20为衡量单位
    font.height = 20 * 14

    for i in range(0, 9):
        # 设置列宽，一个中文等于两个英文等于两个字符，11为字符数，256为衡量单位
        sheet.col(i).width = 11 * 498

    for j in range(0, 128):
        col = sheet.col(j)
        tall_style = xlwt.easyxf('font:height 298;')
        col.set_style(tall_style)

    # 初始化样式
    style0 = xlwt.XFStyle()
    style0.font = font

    # 设置文字模式
    font.num_format_str = '#,##0.00'

    index = len(value)
    for i in range(0, index):
        for j in range(0, len(value[i])):
            sheet.write(i+1, j, str(value[i][j]), style0)
    newb.save(path)
    print("xls格式表格写入数据成功！")


@api.route('/get_report')
def get_report():
    """
    查询当前 可能存在的 report
    :return: jsonify
    """
    info_id = PerfdogData.query.order_by(PerfdogData.info_id.desc()).first().info_id
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


@api.route('/transmission_report', methods=['POST'])
def get_transmission_report():
    """
    用于返回文件流, 后调整为返回 file.read()
    :return: 文件流，以下载
    """
    data = request.get_json(silent=True)

    date = list(data.values())[0]  # 这里不太对， 与上面的 caton_function 里的 dict 套 dict 不一样
    project = list(data.values())[1]  # 这里不太对， 与上面的 caton_function 里的 dict 套 dict 不一样

    report = date + ' ' + project + ' Perfdog 数据对比.xls'
    filePath = os.path.join(baseDir, date)
    os.chdir(filePath)

    if os.path.isfile(os.path.join(filePath, report)):
        read_hey = open(report, 'rb')      # mode='r' encoding='cp936'
        rar_content = read_hey.read()

        read_hey.close()
        return rar_content
    else:
        return 'no xls file'
