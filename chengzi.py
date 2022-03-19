# coding=utf-8
"""
主脚本

flask run --host=0.0.0.0 --port=8086

"""

import os
import sys
from app import create_app, db
from app.models import User, Role, Permission, ProfileData, RiskData

import logging
logging.basicConfig(filename='error.log', level=logging.INFO)

COV = None
if os.environ.get('FLASK_COVERAGE'):  # 放于最开始的位置
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')  # branch=True选项开启分支覆盖度报告，include 选项限制检测的文件在应用包app内
    COV.start()     # 开始


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_content():
    return dict(db=db, User=User, Role=Role,  Permission=Permission, ProfileData=ProfileData, app=app, RiskData=RiskData)


# unit test
@app.cli.command()
def test(coverage):
    """ Run the unit test"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable]+[sys.argv[0]+'.exe'] + sys.argv[1:])

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index/html' % covdir)
        COV.erase()


@app.cli.command()
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    # from werkzeug.contrib.profiler import ProfilerMiddleware
    from werkzeug.middleware.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run(debug=False)


@app.cli.command()
def deploy():       # deploy命令
    """Run development tasks"""

    # 创建或者更新用户角色
    Role.insert_roles()

    # 剩下的

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=8086)
    app.run(debug=True)
