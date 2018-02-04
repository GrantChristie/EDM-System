from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from flask import redirect, url_for, render_template, flash, request, session
from app.forms import LoginForm, AddUser, AddInfo
from werkzeug.urls import url_parse
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
from sqlalchemy import text


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    user_table = pd.read_sql_table('user', db.engine)
    form = AddInfo()
    if form.validate_on_submit():
        info = [form.attendance.data, form.score.data]
        session['info'] = info
        return redirect(url_for('feedback'))
    return render_template('home.html', title='Home', form=form, user_table=user_table)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is already logged in redirect them
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Check that the user exists in the database
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        # Sent them to the page they were trying to access, if it doesn't exist then sent them to the homepage
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/feedback')
def feedback():
    df = pd.read_sql('SELECT * FROM "user"', db.engine)
    """
    f1 = df['attendance'].values
    f2 = df['score'].values
    x = np.matrix(list(zip(f1, f2)))
    kmeans = KMeans(n_clusters=2).fit(x)
    info = session['info']
    if kmeans.predict([info]) == kmeans.labels_[0]:
        feedback = "You are on course to pass."
    else:
        feedback = "Warning, you are on course to fail."
    """
    return render_template('feedback.html', title='Feedback', feedback=df)


@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    # If the user is already logged in redirect them
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = AddUser()
    if form.validate_on_submit():
        user = User(username=form.username.data, attendance=form.attendance.data, score=form.score.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User added')
        return redirect(url_for('adduser'))
    return render_template('adduser.html', title='Add User', form=form)
