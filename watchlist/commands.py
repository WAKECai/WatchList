import click

from watchlist import app, db
from watchlist.models import User, Movie


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988', 'is_read': False},
        {'title': 'Dead Poets Society', 'year': '1989', 'is_read': False},
        {'title': 'A Perfect World', 'year': '1993', 'is_read': False},
        {'title': 'Leon', 'year': '1994', 'is_read': False},
        {'title': 'Mahjong', 'year': '1996', 'is_read': False},
        {'title': 'Swallowtail Butterfly', 'year': '1996', 'is_read': False},
        {'title': 'King of Comedy', 'year': '1999', 'is_read': False},
        {'title': 'Devils on the Doorstep', 'year': '1999', 'is_read': False},
        {'title': 'WALL-E', 'year': '2008', 'is_read': False},
        {'title': 'The Pork of Music', 'year': '2012', 'is_read': False},
        {'title': '头号玩家', 'year': '2018', 'is_read': True},
        {'title': '流浪地球1', 'year': '2012', 'is_read': False},
        {'title': '流浪地球2', 'year': '2023', 'is_read': True},
        {'title': '暮光之城', 'year': '2008', 'is_read': False},
        {'title': '横空出世', 'year': '1999', 'is_read': False},
        {'title': '让子弹飞', 'year': '2010', 'is_read': False},
        {'title': '战狼', 'year': '2015', 'is_read': False},
        {'title': '战狼2', 'year': '2017', 'is_read': False},
        {'title': '蜘蛛侠:纵横宇宙', 'year': '2023', 'is_read': False},
        {'title': '天空之城', 'year': '1986', 'is_read': False},
        {'title': '银河护卫队3', 'year': '2023', 'is_read': False},
        {'title': '肖申克的救赎', 'year': '1994', 'is_read': False},
        {'title': '阿甘正传', 'year': '1994', 'is_read': False},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'], is_read=m['is_read'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')


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
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')

