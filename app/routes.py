from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Student, Programme
from flask import redirect, url_for, render_template, flash, request
from app.forms import LoginForm, AddStudent, AddProgramme
from werkzeug.urls import url_parse
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
from sqlalchemy import text
import matplotlib.pyplot as plt
import datetime

time = datetime.datetime.now()

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    sql = text("SELECT formative_assessment.name, formative_assessment.due_date from formative_assessment inner join student_formative_assessments on student_formative_assessments.formative_assessment_id = formative_assessment.id where student_formative_assessments.submitted = 0 and student_formative_assessments.student_id =" + str(current_user.id) +"and formative_assessment.due_date <='"+time.strftime('%Y-%m-%d')+"'",db.engine)
    result = db.engine.execute(sql)
    assessments = []
    for row in result:
        assessments.append(row)
    return render_template('home.html', title='Home', time=time, assessments=assessments)


@app.route('/login', methods=['GET', 'POST'])
def login():
    student_table = pd.read_sql('SELECT username from student', db.engine)
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
    # Get all the summed scores excluding the current logged in user
    df = pd.read_sql(
        "SELECT SUM(cgs) AS cgssum, SUM(submitted) AS submittedsum from student_formative_assessments inner join formative_assessment on student_formative_assessments.formative_assessment_id=formative_assessment.id where student_id <>" + str(current_user.id) + " and due_date <='" + time.strftime('%Y-%m-%d') + "'group by student_id", db.engine)
    # Get the logged in user's summed scores
    student_data = pd.read_sql("SELECT SUM(cgs) AS cgssum, SUM(submitted) AS submittedsum from student_formative_assessments inner join formative_assessment on student_formative_assessments.formative_assessment_id=formative_assessment.id where student_id =" + str(current_user.id) + " and due_date <='" + time.strftime('%Y-%m-%d') +"'", db.engine)
    f1 = df['cgssum'].values
    f2 = df['submittedsum'].values
    x = np.array(list(zip(f2, f1)))
    kmeans = KMeans(n_clusters=3).fit(x)
    #"""
    plt.scatter(x[:, 0], x[:, 1], c=kmeans.labels_, cmap='rainbow')
    #plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], color='black')
    plt.show()
    #"""
    prediction = kmeans.predict(student_data)
    # If the predicted group is the same group that the best possible result belongs to that is the top group
    if prediction == kmeans.predict([[110, 5]]):
        feedback = "You are in the top group"
    # If the predicted group is the same group the the worst possible result belongs to that is the bottom group
    elif prediction == kmeans.predict([[0, 0]]):
        feedback = "You are in the bottom group"
    else:  # Otherwise prediction belongs in the middle group
        feedback = "You are average"
    return render_template('feedback.html', title='Feedback', feedback=feedback)


@app.route('/addstudent', methods=['GET', 'POST'])
def addstudent():
    form = AddStudent()
    if form.validate_on_submit():
        student = Student(username=form.username.data, f_name=form.f_name.data, l_name=form.l_name.data,
                          dob=form.dob.data, programme_id=form.programme_id.data)
        student.set_password(form.password.data)
        db.session.add(student)
        db.session.commit()
        flash('Student Added')
        return redirect(url_for('addstudent'))
    return render_template('addstudent.html', title='Add Student', form=form)

@app.route('/addprogramme', methods=['GET','POST'])
def addprogramme():
    form = AddProgramme()
    if form.validate_on_submit():
        programme = Programme(programme_name=form.programme_name.data)
        db.session.add(programme)
        db.session.commit()
        flash('Programme Added')
        return redirect(url_for('addprogramme'))
    return render_template('addprogramme.html', title='Add Programme', form=form)


@app.route('/details/<username>')
@login_required
def details(username):
    student = Student.query.filter_by(username=username).first_or_404()
    # Check if the student is trying to access another student's page
    if current_user.username != student.username:
        flash('You do not have permission to view this page')
        return redirect(url_for('home'))

    current = "'" + current_user.username + "'"
    sql = text(
        'select student.username, student.f_name, student.l_name, student.dob, programme.programme_name, student.programme_id, programme.id, student.id from "student" INNER JOIN programme ON student.programme_id = programme.id  WHERE username=' + current + '',
        db.engine)
    result = db.engine.execute(sql)
    details = []
    for detail in result:
        details.append(detail)

    programme = str(details[0][5])
    student_id = str(current_user.id)
    sql = text(
        'select course.id, course.course_name from course inner join programme_courses on programme_courses.course_id=course.id where programme_courses.programme_id=' + programme,
        db.engine)
    result = db.engine.execute(sql)
    courses = []
    summative_assessments = []
    for course in result:
        courses.append(course)

    for course in courses:
        sql = text(
            'select summative_assessment.id, summative_assessment.name, student_summative_assessments.cgs, summative_assessment.course_id from summative_assessment inner join student_summative_assessments on student_summative_assessments.summative_assessment_id=summative_assessment.id where student_id =' + student_id + ' AND summative_assessment.course_id=' + str(
                course[0]), db.engine)
        result = db.engine.execute(sql)
        for assessment in result:
            summative_assessments.append(assessment)

    return render_template('details.html', title='Your Details', student=student, details=details, courses=courses,
                           summative_assessments=summative_assessments)
