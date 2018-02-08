from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Student
from flask import redirect, url_for, render_template, flash, request, session
from app.forms import LoginForm, AddStudent, AddInfo
from werkzeug.urls import url_parse
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
from sqlalchemy import text

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = AddInfo()
    if form.validate_on_submit():
        info = [form.attendance.data, form.score.data]
        session['info'] = info
        return redirect(url_for('feedback'))
    return render_template('home.html', title='Home', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    student_table = pd.read_sql_table('student', db.engine)
    # If the user is already logged in redirect them
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Check that the user exists in the database
        user = Student.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        # Sent them to the page they were trying to access, if it doesn't exist then sent them to the homepage
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form, student_table=student_table)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/feedback')
def feedback():
    df = pd.read_sql('SELECT * FROM "student"', db.engine)
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


@app.route('/addstudent', methods=['GET', 'POST'])
def addstudent():
    # If the user is already logged in redirect them
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = AddStudent()
    if form.validate_on_submit():
        student = Student(username=form.username.data, f_name=form.f_name.data, l_name=form.l_name.data, dob=form.dob.data)
        student.set_password(form.password.data)
        db.session.add(student)
        db.session.commit()
        flash('Student added')
        return redirect(url_for('addstudent'))
    return render_template('addstudent.html', title='Add Student', form=form)


@app.route('/details/<username>')
@login_required
def details(username):
    student = Student.query.filter_by(username=username).first_or_404()
    # Check if the student is trying to access another student's page
    if current_user.username != student.username:
        flash('You do not have permission to view this page')
        return redirect(url_for('home'))
    current = "'"+current_user.username+"'"
    sql = text('select student.username, student.f_name, student.l_name, student.dob, programme.programme_name, student.programme_id, programme.id from "student" INNER JOIN programme ON student.programme_id = programme.id  WHERE username='+current+'', db.engine)
    result = db.engine.execute(sql)
    details = []
    for row in result:
        details.append(row)
    return render_template('details.html', student=student, details=details)
