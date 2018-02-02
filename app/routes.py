from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from flask import redirect, url_for, render_template, flash, request
from app.forms import LoginForm, AddUser
from werkzeug.urls import url_parse
import numpy as np
from sklearn.cluster import KMeans

@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
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
    return render_template('feedback.html', title='Feedback')

@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
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