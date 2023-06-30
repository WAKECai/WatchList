from flask import Flask, render_template, redirect, url_for, request, flash
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy     # 导入拓展类
import os
import sys
import click
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_login import current_user
from flask_login import UserMixin

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
# 设置签名所需的密匙
app.config['SECRET_KEY'] = 'dev'


# 定义两个类
class User(db.Model, UserMixin):   # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)    # 主键
    name = db.Column(db.String(20))     # 名字
    username = db.Column(db.String(20))     # 用户名
    password_hash = db.Column(db.String(128))   # 密码散列值

    def set_password(self, password):   # 用来设置密码的方法， 接受密码作为参数
        self.password_hash = generate_password_hash(password)   # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用来验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)    # 返回布尔值


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))    # 电影标题
    year = db.Column(db.String(10))  # 电影年份


# 模版上下处理函数：后面我们创建的任意一个模板，都可以在模板中直接使用 user 变量。
@app.context_processor
def inject_user():    # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)    # 需要返回字典，等同于返回 return {'user':user}


@app.context_processor
def inject_function():
    # 定义要引入的函数

    # 判断是否为中文字符
    def is_chinese(char):
        if '\u4e00' <= char <= '\u9fa5':
            return True
        else:
            return False

    # 判断是否包含中文字符
    def contains_chinese(text):
        for char in text:
            if is_chinese(char):
                return True
        return False

    return {
        'contains_chinese': contains_chinese
    }


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


# 编写命令来创建管理员账号
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)    # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:    # 如果当前用户未认证
            return redirect(url_for('index'))
        # 获取表单数据
        title = request.form.get('title')   # 传入表单对应输入字段的name值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')     # 显示错误提示
            return redirect(url_for('index'))   # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)    # 创建记录
        db.session.add(movie)   # 添加到数据库对话
        db.session.commit()     # 提交数据库对话
        flash('Item created.')  # 显示成功创建的提示
        return redirect(url_for('index'))   # 重定向回主页

    movies = Movie.query.all()  # 读取所有电影记录
    return render_template('index.html', movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required    # 登录保护
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        if not title or not year or len(year) >= 4 or len(title) > 60:
            flash('Invalid input.')     # 显示错误提示
            return redirect(url_for('index'))   # 重定向回对应的编辑页面
        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required    # 登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


@app.route('/test')
def test_url_for():
    # 下面是一些调用示例
    print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
    print(url_for('user_page', name='peter'))
    print(url_for('test_url_for'))

    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到URL后面
    print(url_for('test_url_for', num=2))
    return 'Test page'


# Not Found 错误
@app.errorhandler(404)
def page_not_found(e):
    # user = User.query.first()
    return render_template('404.html'), 404


# 初始化Flask-Login
login_manager = LoginManager(app)    # 实例化拓展类
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):    # 创建用户加载回调函数，接受用户ID作为参数
    user = User.query.get(int(user_id))    # 用ID作为user模型的主键查询对应的用户
    return user    # 返回用户对象


# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)    # 登录用户
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')


# 登出
@app.route('/logout')
@login_required    # 用于视图保护
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))


# 设置页面，支持修改用户的名字
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Setting updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')


if __name__ == '__main__':
    app.run(debug=True)

