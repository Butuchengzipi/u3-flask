# coding=utf-8

"""
Supply Commit
"""

import os
import shutil  # copy文件
import zipfile

from flask import flash
from ..models import ProfileData, Info
from .. import db

baseDir = r'D:\\Performance'
analysisDir = r'D:\\Performance\\analysis\\'
debug_output = 'debug_output.rar'
timerAnalyse = 'AnalyseTimer.py'
createFlameGraph = 'FlameGraph.py'
flameGraphSupport = 'flamegraph.pl'


def unzip_file(directory):
    """ 解压缩, 当前只支持 .rar 格式 """
    os.chdir(directory)

    rar = zipfile.ZipFile('debug_output.rar', mode='r')  # 这里需要填入需要解压的文件名

    # rar压缩包的算法并不对外公开,
    # ************     需要将unrar.exe复制到运行环境目录下      ***************
    rar.extractall()  # 若需要生成在固定目录下，则可以在 extractall() 中填入 os.path.splitext(filename)[0]
    rar.close()


def copy_debug_output(directory):
    """ 复制 debug_output! """
    """ 这里还不能直接复制，若直接复制。生成的目录下会堆积若干 debug_output.rar 文件，影响后续的文件处理"""
    """ 所以，这里需要移动文件，而非复制文件！！！ """
    os.chdir(baseDir)
    try:
        shutil.move(debug_output, directory)  # copy 复制文件到 目录或文件中， copyfile则是复制内容到另一个文件中
    except Exception as e:
        print(e)


def copy_analysisFile(directory):
    """ 复制脚本及所需文件，并调用执行函数 """
    os.chdir(analysisDir)
    try:
        shutil.copy(timerAnalyse, directory)  # copy 复制文件到 目录或文件中， copyfile则是复制内容到另一个文件中
        shutil.copy(createFlameGraph, directory)
        shutil.copy(flameGraphSupport, directory)
    except Exception as e:
        print(e)
    os.chdir(directory)
    run_flameGraph()
    run_analyseTimer()


def run_analyseTimer():
    """ run .. analyseTimer.py """
    try:
        os.system('py -2 AnalyseTimer.py')  # 需要正确添加对应 的python版本 进注册表，有疑问可以百度
    except Exception as e:
        print(e)


def run_flameGraph():
    """ run .. flameGraph.py """
    try:
        os.system('py -2 FlameGraph.py')
    except Exception as e:
        print(e)


def cre_tarfile(folder):
    """ # 创建压缩文件 """
    targetDir = os.path.join(baseDir, folder.split(' ')[0])  # 目标路径
    os.chdir(targetDir)

    try:
        zipFile = shutil.make_archive(os.path.join(baseDir, folder), format='zip', root_dir=targetDir)
        shutil.move(zipFile, targetDir)  # 移动文件,  ret为文件的完整路径， targetDir为目标路径
        return True
    except Exception as e:
        print(e)
        return False


def analyse_excel(date, project, branch, model, test_content, frame, remark, high_path):
    """ 分析生成的 csv 文件 """
    if is_Repeat(date, project, branch, model, test_content, frame, remark):
        # flash('你已经提交过相关数据了......')
        print('Have commited...')

    else:
        try:
            # 预先提交 info， 防止数据重复
            info = Info(date=date,
                        project=project,
                        branch=branch,
                        model=model,
                        test_content=test_content,
                        frame=frame,
                        remark=remark)
            db.session.add(info)
            db.session.commit()

            # 拿到本次提交的 外链 id
            info_id = Info.query.filter_by(date=date,
                                           project=project,
                                           branch=branch,
                                           model=model,
                                           test_content=test_content,
                                           frame=frame,
                                           remark=remark).first().id
            print('*************** info_id ****************', info_id)
            data = ProfileData()
            # root：表示当前遍历到哪一级目录了，目录的名字是谁
            # dirs：表示root下有哪些子目录
            # files：表示root下边有几个文件
            for root, dirs, files in os.walk(os.path.join(baseDir, date)):
                for file in files:
                    # os.path.basename 获取文件名
                    if os.path.basename(os.path.join(root, file)) == 'python_timer_root_function_statistics.csv':
                        # 找到对应的 csv 文件，找到生成的卡顿项
                        file = open(file, 'r')
                        for line in file:
                            # 遍历 文件的每一行数据
                            for i in range(len(line.split(','))):
                                filePath = os.path.join(baseDir,
                                                        date,
                                                        high_path,
                                                        model,
                                                        test_content,
                                                        frame,
                                                        'debug_output')  # 文件的保存路径, 这里刨除文件名

                                filename = line.split(',')[5]  # 找到记录的 timer文件
                                profileFilename = filename.split('.timer')[0] + '.svg'

                                data = ProfileData(function=line.split(',')[1],
                                                   frequency=line.split(',')[2],
                                                   delaytime=line.split(',')[3],
                                                   totalDelaytime=line.split(',')[4],
                                                   profileFilename=profileFilename,
                                                   filePath=filePath,
                                                   info_id=info_id)

                            db.session.add(data)
                            db.session.commit()
                        file.close()
            flash('Data have been uploaded.')
        except Exception as e:
            print(e)
            db.session.rollback()  # 若有问题，回退
        return 'OK...'


def is_Repeat(date, project, branch, model, test_content, frame, remark):
    """ 查询内容是否有重复 """
    info = Info.query.filter_by(date=date,
                                project=project,
                                branch=branch,
                                model=model,
                                test_content=test_content,
                                frame=frame,
                                remark=remark).first()
    if info is None:
        return False
    else:
        return True


def find_Info_id(date, project, branch):
    """ 查询info id """
    info = Info.query.filter_by(date=date,
                                project=project,
                                branch=branch).first().id
    return info


def dirOperations(date, project, branch, model, test_content, frame):
    """ 生成目录，返回相应的文件路径 """
    high_path = date + ' ' + project + ' ' + branch     # basedir 目录下，第二级目录

    os.chdir(baseDir)
    try:
        if os.path.isdir(date):                      # 总目录
            os.chdir(date)
            if os.path.isdir(high_path):             # 判断 有无 本次提交时间的目录
                os.chdir(high_path)
                if os.path.isdir(model):             # 判断 有无 测试机目录
                    os.chdir(model)
                    if os.path.isdir(test_content):  # 判断 有无 本次测试内容的目录
                        os.chdir(test_content)
                        if os.path.isdir(frame):     # 判断 有无 框架 目录
                            os.chdir(frame)
                        else:
                            os.mkdir(frame)
                    else:
                        os.makedirs(test_content + '\\' + frame)
                else:
                    os.makedirs(model + '\\' + test_content + '\\' + frame)
            else:
                os.makedirs(high_path + '\\' + model + '\\' + test_content + '\\' + frame)

        else:
            path = date + '\\' + high_path + '\\' + model + '\\' + test_content + '\\' + frame
            os.makedirs(path)  # 创建多级目录
    except Exception as e:
        print(e)

    savePath = os.path.join(baseDir + '\\' + date + '\\' + high_path + '\\' + model + '\\' + test_content + '\\' + frame)

    return savePath, high_path
