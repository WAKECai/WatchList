from flask import Flask, render_template, redirect, url_for
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy     # 导入拓展类
import os
import sys
import click


app = Flask(__name__)
WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)


# 模版上下处理函数：后面我们创建的任意一个模板，都可以在模板中直接使用 user 变量。
@app.context_processor
def inject_user():    # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)    # 需要返回字典，等同于返回 return {'user':user}


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')     # 输出提示信息


# 自定义命令forge
@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    name = 'Yu Chen Cong' \
           ''
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
        {'title': '密室逃脱1', 'year': 'Unknown'},
        {'title': '头号玩家', 'year': 'Unknown'},
        {'title': '火星救援', 'year': 'Unknown'},
        {'title': '流浪地球1', 'year': 'Unknown'},
        {'title': '流浪地球2', 'year': 'Unknown'},
        {'title': '暮光之城', 'year': 'Unknown'},
        {'title': '横空出世', 'year': 'Unknown'},
        {'title': '让子弹飞', 'year': 'Unknown'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')


@app.route('/')
def index():
    # user = User.query.first()   # 读取用户记录
    movies = Movie.query.all()  # 读取所有电影记录
    return render_template('index.html', movies=movies)


@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}'


@app.route('/test')
def test_url_for():
    # 下面是一些调用示例
    print(url_for('hello'))
    print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
    print(url_for('user_page', name='peter'))
    print(url_for('test_url_for'))

    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到URL后面
    print(url_for('test_url_for', num=2))
    return 'Test page'


@app.errorhandler(404)
def page_not_found(e):
    # user = User.query.first()
    return render_template('404.html'), 404


class User(db.Model):   # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)    # 主键
    name = db.Column(db.String(20))     # 名字


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))    # 电影标题
    year = db.Column(db.String(10))  # 电影年份


if __name__ == '__main__':
    app.run(debug=True)

