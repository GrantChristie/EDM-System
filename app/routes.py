from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Student, Programme, Course, FormativeAssessment, SummativeAssessment
from flask import render_template, request
from app.forms import LoginForm, AddStudent, AddProgramme, AddCourse, AddFormativeAssessment, AddSummativeAssessment, \
    AddCourseToProgramme, AddFormativeResult, AddSummativeResult
from werkzeug.urls import url_parse
from sklearn.cluster import KMeans
from sqlalchemy import text
from app.helpers import *
import datetime
import numpy as np
import pandas as pd
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


time = datetime.datetime.now()


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # Get student's overdue formative assessments for each course
    sql = text(
        "SELECT formative_assessment.name, formative_assessment.due_date, course.course_name from formative_assessment inner join student_formative_assessments on student_formative_assessments.formative_assessment_id = formative_assessment.id inner join course on formative_assessment.course_id = course.id where student_formative_assessments.submitted = 0 and student_formative_assessments.student_id =" + str(
            current_user.id) + "and formative_assessment.due_date <='" + time.strftime('%Y-%m-%d') + "'", db.engine)
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
    flash("You are logged out")
    return redirect(url_for('login'))


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
    programme = str(student.programme_id)
    student_id = str(current_user.id)

    course_table = pd.read_sql('select course.id, course.course_name, course.level, course.sub_session from course inner join programme_courses on programme_courses.course_id=course.id where programme_courses.programme_id=' + programme + 'order by course.level, course.sub_session',
        db.engine)

    courses = []
    summative_assessments = []

    for course in course_table.values:
        courses.append(course)

    for course in courses:
        sql = text(
            'select summative_assessment.id, summative_assessment.name, student_summative_assessments.cgs, summative_assessment.course_id, summative_assessment.contribution from summative_assessment inner join student_summative_assessments on student_summative_assessments.summative_assessment_id=summative_assessment.id where student_id =' + student_id + ' AND summative_assessment.course_id=' + str(
                course[0]), db.engine)
        result = db.engine.execute(sql)
        for assessment in result:
            summative_assessments.append(assessment)
    return render_template('details.html', title='Your Details', student=student, details=details, courses=courses,summative_assessments=summative_assessments)


@app.route('/coursefeedback/<course>')
@login_required
def coursefeedback(course):
    # Get all the summed scores excluding the current logged in user
    df = pd.read_sql(
        "SELECT SUM(cgs) AS cgssum, SUM(submitted) AS submittedsum from student_formative_assessments inner join formative_assessment on student_formative_assessments.formative_assessment_id=formative_assessment.id where student_id <>" + str(
            current_user.id) + " and due_date <='" + time.strftime(
            '%Y-%m-%d') + "' and formative_assessment.course_id =" + course + "group by student_id", db.engine)
    # Get the logged in user's summed scores
    student_data = pd.read_sql(
        "SELECT SUM(cgs) AS cgssum, SUM(submitted) AS submittedsum from student_formative_assessments inner join formative_assessment on student_formative_assessments.formative_assessment_id=formative_assessment.id where student_id =" + str(
            current_user.id) + " and due_date <='" + time.strftime(
            '%Y-%m-%d') + "' and formative_assessment.course_id =" + course, db.engine)
    f1 = df['cgssum'].values
    f2 = df['submittedsum'].values

    x = np.array(list(zip(f2, f1)))
    kmeans = KMeans(n_clusters=3).fit(x)
    prediction = kmeans.predict([[student_data['submittedsum'].values[0],student_data['cgssum'].values[0]]])

    img = io.BytesIO()
    plt.clf()
    plt.scatter(x[:, 0], x[:, 1], c=kmeans.labels_, cmap='rainbow')
    plt.plot(student_data['submittedsum'].values,student_data['cgssum'].values, 'y*', label='You')
    plt.xticks(np.arange(min(f2), max(f2)+1, 1))
    plt.yticks(np.arange(min(f1), max(f1)+1, 10))
    plt.xlabel('Total Submitted')
    plt.ylabel('Total CGS Score')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    # plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], color='black')
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    # If the predicted group is the same group that the best possible result belongs to that is the top group
    if prediction == kmeans.predict([[5, 110]]):
        feedback = "You are in the top group"
    # If the predicted group is the same group the the worst possible result belongs to that is the bottom group
    elif prediction == kmeans.predict([[0, 0]]):
        feedback = "You are in the bottom group"
    else:  # Otherwise prediction belongs in the middle group
        feedback = "You are average"
    return render_template('feedback.html', title='Feedback', feedback=feedback, plot_url=plot_url)


@app.route('/programmefeedback/<username>')
@login_required
def programmefeedback(username):
    student = Student.query.filter_by(username=username).first_or_404()
    # Check if the student is trying to access another student's page
    if current_user.username != student.username:
        flash('You do not have permission to view this page')
        return redirect(url_for('home'))

    student_id = str(student.id)
    student_list = pd.read_sql("SELECT id FROM student where username <> 'admin'", db.engine)

    level1grades = []
    level2grades = []

    #start of loop
    for id in student_list['id'].values:
        id = str(id)
        level_1_scores = pd.read_sql('SELECT course.course_name as course_name, credits, '
                                     'sum(contribution * cgs) as course_grade '
                                     'from student_summative_assessments '
                                     'inner JOIN summative_assessment '
                                     'on student_summative_assessments.summative_assessment_id = summative_assessment.id '
                                     'inner JOIN course '
                                     'on summative_assessment.course_id = course.id '
                                     'inner JOIN programme_courses on course.id = programme_courses.course_id '
                                     'where programme_courses.programme_id = 1 '
                                     'AND student_id =' + id + 'and course.level = 1 group by course.id',
                                     db.engine)
        total_level1_credits = level_1_scores['credits'].sum()
        level1_results = []

        for course_credits, grade in zip(level_1_scores['credits'].values, level_1_scores['course_grade'].values):
            level1_results.append(calculategpa(grade, course_credits, total_level1_credits))
        level1grade = (sum(level1_results))

        # Prevent second sql statement from running if the student has no first year results
        if level1grade == 0:
            continue

        level_2_scores = pd.read_sql('SELECT course.course_name as course_name, credits, '
                                     'sum(contribution * cgs) as course_grade '
                                     'from student_summative_assessments '
                                     'inner JOIN summative_assessment '
                                     'on student_summative_assessments.summative_assessment_id = summative_assessment.id '
                                     'inner JOIN course '
                                     'on summative_assessment.course_id = course.id '
                                     'inner JOIN programme_courses on course.id = programme_courses.course_id '
                                     'where programme_courses.programme_id = 1 '
                                     'AND student_id =' + id + 'and course.level = 2 group by course.id',
                                     db.engine)
        total_level2_credits = level_2_scores['credits'].sum()
        level2_results = []
        for course_credits, grade in zip(level_2_scores['credits'].values, level_2_scores['course_grade'].values):
            level2_results.append(calculategpa(grade, course_credits, total_level2_credits))

        level2grade = (sum(level2_results))
        if level1grade != 0 or level2grade != 0:
            level1grades.append(level1grade)
            level2grades.append(level2grade)
    #end of loop

    level_1_scores = pd.read_sql('SELECT course.course_name as course_name, credits, '
                                 'sum(contribution * cgs) as course_grade '
                                 'from student_summative_assessments '
                                 'inner JOIN summative_assessment '
                                 'on student_summative_assessments.summative_assessment_id = summative_assessment.id '
                                 'inner JOIN course '
                                 'on summative_assessment.course_id = course.id '
                                 'inner JOIN programme_courses on course.id = programme_courses.course_id '
                                 'where programme_courses.programme_id = 1 '
                                 'AND student_id =' + student_id + 'and course.level = 1 group by course.id', db.engine)

    total_level1_credits = level_1_scores['credits'].sum()
    student_l1_results = []

    for course_credits, grade in zip(level_1_scores['credits'].values, level_1_scores['course_grade'].values):
        student_l1_results.append(calculategpa(grade, course_credits, total_level1_credits))

    level1grade = gradebandcheck(sum(student_l1_results))

    level_2_scores = pd.read_sql('SELECT course.course_name as course_name, credits, '
                                 'sum(contribution * cgs) as course_grade '
                                 'from student_summative_assessments '
                                 'inner JOIN summative_assessment '
                                 'on student_summative_assessments.summative_assessment_id = summative_assessment.id '
                                 'inner JOIN course '
                                 'on summative_assessment.course_id = course.id '
                                 'inner JOIN programme_courses on course.id = programme_courses.course_id '
                                 'where programme_courses.programme_id = 1 '
                                 'AND student_id =' + student_id + 'and course.level = 2 group by course.id', db.engine)

    total_level2_credits = level_2_scores['credits'].sum()
    student_l2_results = []

    for course_credits, grade in zip(level_2_scores['credits'].values, level_2_scores['course_grade'].values):
        student_l2_results.append(calculategpa(grade, course_credits, total_level2_credits))

    level2grade = gradebandcheck(sum(student_l2_results))
    mock_honours_grade = degreeclassification((sum(student_l1_results) * 0.3) + (sum(student_l2_results) * 0.7))
    x = np.array(list(zip(level1grades, level2grades)))
    kmeans = KMeans(n_clusters=5).fit(x)

    img = io.BytesIO()
    plt.clf()
    plt.scatter(x[:, 0], x[:, 1], c=kmeans.labels_, cmap='rainbow')
    plt.plot(sum(student_l1_results),sum(student_l2_results) , 'ko', label='You', markersize=7)
    #plt.xticks(np.arange(0, 22+1, 2))
    #plt.yticks(np.arange(0, 22+1, 2))
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], color='black', marker='+')#REMOVE IN FINAL VERSION
    plt.xlabel('Level 1 Grade')
    plt.ylabel('Level 2 Grade')
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    prediction = kmeans.predict([[sum(student_l1_results),sum(student_l2_results)]])
    if prediction == kmeans.predict([[max(level1grades),max(level2grades)]]):
        feedback = "You are in the top performers for both year 1 and year 2, well done!"
    elif prediction == kmeans.predict([[min(level1grades),max(level2grades)]]):
        feedback = "You have improved from year 1 and are now one of the best performers in year 2."
    elif prediction == kmeans.predict([[min(level1grades),min(level2grades)]]):
        feedback = "You are in the worst performers for both year 1 and year 2."
    elif prediction == kmeans.predict([[max(level1grades), min(level2grades)]]):
        feedback = "You were one of the top performers in year 1 but your results have gotten worse compared to your peers."
    else:
        feedback = "You are performing averagely compared to your peers"

    return render_template('programmefeedback.html', title='Programme Feedback', plot_url=plot_url,
                           level1grade=level1grade, level2grade=level2grade, mock_honours_grade=mock_honours_grade,
                           feedback=feedback)

@app.route('/addstudent', methods=['GET', 'POST'])
@login_required
def addstudent():
    admincheck(current_user.username)
    df = pd.read_sql('select * from programme', db.engine)
    ids = df['id'].values
    names = df['programme_name'].values
    form = AddStudent()
    form.programme_id.choices = [(x, y) for x, y in zip(ids, names)]
    if form.validate_on_submit():
        student = Student(username=form.username.data, f_name=form.f_name.data, l_name=form.l_name.data,
                          dob=form.dob.data, programme_id=form.programme_id.data)
        student.set_password(form.password.data)
        db.session.add(student)
        db.session.commit()
        flash('Student Added')
        return redirect(url_for('addstudent'))
    return render_template('admin/addstudent.html', title='Add Student', form=form)


@app.route('/addprogramme', methods=['GET', 'POST'])
@login_required
def addprogramme():
    admincheck(current_user.username)
    form = AddProgramme()
    if form.validate_on_submit():
        programme = Programme(programme_name=form.programme_name.data)
        db.session.add(programme)
        db.session.commit()
        flash('Programme Added')
        return redirect(url_for('addprogramme'))
    return render_template('admin/addprogramme.html', title='Add Programme', form=form)


@app.route('/addcourse', methods=['GET', 'POST'])
@login_required
def addcourse():
    admincheck(current_user.username)
    form = AddCourse()
    if form.validate_on_submit():
        course = Course(course_name=form.course_name.data, level=form.level.data, credits=form.credits.data)
        db.session.add(course)
        db.session.commit()
        flash('Course Added')
        return redirect(url_for('addcourse'))
    return render_template('admin/addcourse.html', title='Add Course', form=form)


@app.route('/addformativeassessment', methods=['GET', 'POST'])
@login_required
def addformativeassessment():
    admincheck(current_user.username)
    df = pd.read_sql('select id, course_name from course', db.engine)
    ids = df['id'].values
    course_names = df['course_name'].values
    form = AddFormativeAssessment()
    form.course_id.choices = [(x, y) for x, y in zip(ids, course_names)]
    if form.validate_on_submit():
        formativeassessment = FormativeAssessment(name=form.name.data, due_date=form.due_date.data,
                                                  course_id=form.course_id.data)
        db.session.add(formativeassessment)
        db.session.commit()
        flash('Formative Assessment Added')
        return redirect(url_for('addformativeassessment'))
    return render_template('admin/addformativeassessment.html', title='Add Formative Assessment', form=form)


@app.route('/addsummativeassessment', methods=['GET', 'POST'])
@login_required
def addsummativeassessment():
    admincheck(current_user.username)
    df = pd.read_sql('select id, course_name from course', db.engine)
    ids = df['id'].values
    course_names = df['course_name'].values
    form = AddSummativeAssessment()
    form.course_id.choices = [(x, y) for x, y in zip(ids, course_names)]
    if form.validate_on_submit():
        summativeassessment = SummativeAssessment(name=form.name.data, due_date=form.due_date.data,
                                                  contribution=form.contribution.data, course_id=form.course_id.data)
        db.session.add(summativeassessment)
        db.session.commit()
        flash('Summative Assessment Added')
        return redirect(url_for('addsummativeassessment'))
    return render_template('admin/addsummativeassessment.html', title='Add Formative Assessment', form=form)


@app.route('/addcoursetoprogramme', methods=['GET', 'POST'])
@login_required
def addcoursetoprogramme():
    admincheck(current_user.username)
    programmes = pd.read_sql('select * from programme', db.engine)
    courses = pd.read_sql('select * from course', db.engine)
    programme_ids = programmes['id'].values
    programme_names = programmes['programme_name'].values
    course_ids = courses['id'].values
    course_names = courses['course_name'].values
    form = AddCourseToProgramme()
    form.programme_id.choices = [(x, y) for x, y in zip(programme_ids, programme_names)]
    form.course_id.choices = [(x, y) for x, y in zip(course_ids, course_names)]
    if form.validate_on_submit():
        programme_id = str(form.programme_id.data)
        course_id = str(form.course_id.data)
        exists = pd.read_sql(
            'SELECT EXISTS (SELECT * FROM PROGRAMME_COURSES WHERE PROGRAMME_ID =' + programme_id + ' AND COURSE_ID=' + course_id + ')',
            db.engine)
        if (exists['exists'][0] == True):
            flash('Could not add course as course already exists in that programme')
        else:
            db.engine.execute(text(
                'INSERT INTO programme_courses(programme_id, course_id) VALUES (' + programme_id + ',' + course_id + ')'))
            flash('Course added to programme')
        return redirect(url_for('addcoursetoprogramme'))
    return render_template('admin/addcoursetoprogramme.html', title='Add Course to Programme', form=form)


@app.route('/addformativeresult', methods=['GET', 'POST'])
@login_required
def addformativeresult():
    admincheck(current_user.username)
    students = pd.read_sql('SELECT * FROM STUDENT', db.engine)
    formative_assessments = pd.read_sql(
        'SELECT FORMATIVE_ASSESSMENT.ID, FORMATIVE_ASSESSMENT.NAME, COURSE.COURSE_NAME FROM FORMATIVE_ASSESSMENT INNER JOIN COURSE ON FORMATIVE_ASSESSMENT.COURSE_ID = COURSE.ID',
        db.engine)
    student_ids = students['id'].values
    usernames = students['username'].values
    formative_assessment_ids = formative_assessments['id'].values
    formative_assessment_names = formative_assessments['name'].values
    course_names = formative_assessments['course_name'].values
    names = [x[0] + ": " + x[1] for x in zip(course_names, formative_assessment_names)]
    form = AddFormativeResult()
    form.student_id.choices = [(x, y) for x, y in zip(student_ids, usernames)]
    form.formative_assessment_id.choices = [(x, y) for x, y in zip(formative_assessment_ids, names)]
    if form.validate_on_submit():
        formative_assessment_id = str(form.formative_assessment_id.data)
        student_id = str(form.student_id.data)
        exists = pd.read_sql(
            'SELECT EXISTS (SELECT * FROM STUDENT_FORMATIVE_ASSESSMENTS WHERE student_id =' + student_id + ' and formative_assessment_id =' + formative_assessment_id + ')',
            db.engine)
        if exists['exists'][0] == True:
            flash('That user already has a result for that assessment')
        else:
            programme_ids = pd.read_sql(
                'SELECT programme_id FROM formative_assessment inner join course on course_id=course.id inner join programme_courses on course.id = programme_courses.course_id  where formative_assessment.id=' + formative_assessment_id,
                db.engine)['programme_id'].values
            for programme_id in programme_ids:
                if pd.read_sql(
                        'SELECT EXISTS (SELECT * FROM STUDENT WHERE ID=' + student_id + 'and programme_id=' + str(
                                programme_id) + ')', db.engine)['exists'][0] == True:
                    db.engine.execute(text(
                        'INSERT INTO student_formative_assessments (student_id, formative_assessment_id, cgs, submitted) VALUES (' + student_id + ',' + formative_assessment_id + ',' + str(
                            form.cgs.data) + ',' + str(form.submitted.data) + ')'))
                    flash('Result added')
                    break
                else:
                    flash('User is not enrolled on that course')
        return redirect(url_for('addformativeresult'))
    return render_template('admin/addformativeresult.html', title='Add Formative Result', form=form)


@app.route('/addsummativeresult', methods=['GET', 'POST'])
@login_required
def addsummativeresult():
    admincheck(current_user.username)
    students = pd.read_sql('SELECT * FROM STUDENT', db.engine)
    summative_assessments = pd.read_sql(
        'SELECT SUMMATIVE_ASSESSMENT.ID, SUMMATIVE_ASSESSMENT.NAME, COURSE.COURSE_NAME FROM SUMMATIVE_ASSESSMENT INNER JOIN COURSE ON SUMMATIVE_ASSESSMENT.COURSE_ID = COURSE.ID',
        db.engine)
    student_ids = students['id'].values
    usernames = students['username'].values
    summative_assessment_ids = summative_assessments['id'].values
    summativee_assessment_names = summative_assessments['name'].values
    course_names = summative_assessments['course_name'].values
    names = [x[0] + ": " + x[1] for x in zip(course_names, summativee_assessment_names)]
    form = AddSummativeResult()
    form.student_id.choices = [(x, y) for x, y in zip(student_ids, usernames)]
    form.summative_assessment_id.choices = [(x, y) for x, y in zip(summative_assessment_ids, names)]
    if form.validate_on_submit():
        student_id = str(form.student_id.data)
        summative_assessment_id = str(form.summative_assessment_id.data)
        exists = pd.read_sql(
            'SELECT EXISTS (SELECT * FROM STUDENT_SUMMATIVE_ASSESSMENTS WHERE student_id =' + student_id + ' and summative_assessment_id =' + summative_assessment_id + ')',
            db.engine)
        if exists['exists'][0] == True:
            flash('That user already has a result for that assessment')
        else:
            programme_ids = pd.read_sql(
                'SELECT programme_id FROM summative_assessment inner join course on course_id=course.id inner join programme_courses on course.id = programme_courses.course_id  where summative_assessment.id=' + summative_assessment_id,
                db.engine)['programme_id'].values
            for programme_id in programme_ids:
                if pd.read_sql(
                        'SELECT EXISTS (SELECT * FROM STUDENT WHERE ID=' + student_id + 'and programme_id=' + str(
                                programme_id) + ')', db.engine)['exists'][0] == True:
                    db.engine.execute(text(
                        'INSERT INTO student_summative_assessments (student_id, summative_assessment_id, cgs, submitted) VALUES (' + student_id + ',' + summative_assessment_id + ',' + str(
                            form.cgs.data) + ',' + str(form.submitted.data) + ')'))
                    flash('Result added')
                    break
                else:
                    flash('User is not enrolled on that course')
        return redirect(url_for('addsummativeresult'))
    return render_template('admin/addsummativeresult.html', title='Add Summative Result', form=form)

