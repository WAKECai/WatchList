from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie


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
        if not title or not year or len(year) > 4 or len(title) > 60:
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
