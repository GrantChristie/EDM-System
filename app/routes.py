from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Student, Programme, Course, FormativeAssessment, SummativeAssessment
from flask import render_template, request
from app.forms import LoginForm, AddStudent, AddProgramme, AddCourse, AddFormativeAssessment, AddSummativeAssessment, \
    AddCourseToProgramme, AddFormativeResult, AddSummativeResult, SelectFormativeCourse, SelectYear, SelectCourse
from werkzeug.urls import url_parse
from sklearn.cluster import KMeans
from sqlalchemy import text
from app.helpers import *
from sklearn import linear_model
from sklearn.naive_bayes import GaussianNB
from sympy.solvers import solve
from sympy import Symbol, Eq
import datetime
import pandas as pd
import math
import io
import base64
import matplotlib
import bisect
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])
time = datetime.datetime.now()
time = datetime.datetime(2014, 11, 30)


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    time2 = time + datetime.timedelta(days=7)
    upcoming_formative_assessments = pd.read_sql("SELECT formative_assessment.name, formative_assessment.due_date, course.course_name from formative_assessment inner join student_formative_assessments on student_formative_assessments.formative_assessment_id = formative_assessment.id inner join course on formative_assessment.course_id = course.id where student_formative_assessments.submitted is NULL and student_formative_assessments.student_id =" + str(
            current_user.id) + "and formative_assessment.due_date >='" + time.strftime('%Y-%m-%d') + "' and formative_assessment.due_date <='" + time2.strftime('%Y-%m-%d') + "'", db.engine)

    upcoming_summative_assessments = pd.read_sql("SELECT summative_assessment.name, summative_assessment.due_date, course.course_name from summative_assessment inner join student_summative_assessments on student_summative_assessments.summative_assessment_id = summative_assessment.id inner join course on summative_assessment.course_id = course.id where student_summative_assessments.submitted is NULL and student_summative_assessments.student_id =" + str(
            current_user.id) + "and summative_assessment.due_date >='" + time.strftime('%Y-%m-%d') + "' and summative_assessment.due_date <='" + time2.strftime('%Y-%m-%d') + "'", db.engine)
    if upcoming_summative_assessments.empty:
        upcoming_summative_message = ""
    else:
        upcoming_summative_message = "The following summative assessments are due soon:"
    if upcoming_formative_assessments.empty:
        upcoming_formative_message = ""
    else:
        upcoming_formative_message = "The following formative assessments are due soon:"
    # Get student's overdue formative assessments for each course
    overdue_formative = pd.read_sql(
        "SELECT formative_assessment.name, formative_assessment.due_date, course.course_name from formative_assessment inner join student_formative_assessments on student_formative_assessments.formative_assessment_id = formative_assessment.id inner join course on formative_assessment.course_id = course.id where student_formative_assessments.submitted is NULL and student_formative_assessments.student_id =" + str(
            current_user.id) + "and formative_assessment.due_date <'" + time.strftime('%Y-%m-%d') + "'", db.engine)
    if overdue_formative.empty:
        formative_message = "You have no overdue formative assessments."
    else:
        formative_message = "The following formative assessments are overdue:"

    overdue_summative = pd.read_sql(
        "SELECT summative_assessment.name, summative_assessment.due_date, course.course_name from summative_assessment inner join student_summative_assessments on student_summative_assessments.summative_assessment_id = summative_assessment.id inner join course on summative_assessment.course_id = course.id where student_summative_assessments.submitted is NULL and student_summative_assessments.student_id =" + str(
            current_user.id) + "and summative_assessment.due_date <'" + time.strftime('%Y-%m-%d') + "'", db.engine)
    if overdue_summative.empty:
        summative_message = "You have no overdue summative assessments."
    else:
        summative_message = "The following summative assessments are overdue:"

    return render_template('home.html', title='Home', time=time, formative_message=formative_message,
                           overdue_formative=overdue_formative, summative_message=summative_message,
                           overdue_summative=overdue_summative,
                           upcoming_summative_message=upcoming_summative_message,
                           upcoming_formative_message=upcoming_formative_message,
                           upcoming_summative_assessments=upcoming_summative_assessments,
                           upcoming_formative_assessments=upcoming_formative_assessments)


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

    details = pd.read_sql('select student.username, student.f_name, student.l_name, student.dob, student.year, programme.programme_name '
                          'from "student" INNER JOIN programme ON student.programme_id = programme.id  '
                          'WHERE username=' + current + '', db.engine)

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
    return render_template('details.html', title='Your Details', student=student, details=details, courses=courses, summative_assessments=summative_assessments)


@app.route('/coursefeedback/<username>', methods=['GET', 'POST'])
@login_required
def coursefeedback(username):
    student = Student.query.filter_by(username=username).first_or_404()
    # Check if the student is trying to access another student's page
    if current_user.username != student.username:
        flash('You do not have permission to view this page')
        return redirect(url_for('home'))

    programme = str(student.programme_id)
    # Get a list of courses the student can select to get feedback for
    courses = pd.read_sql('select course.id, course.course_name, course.level, course.sub_session '
                          'from course inner join programme_courses on programme_courses.course_id=course.id '
                          'where programme_courses.programme_id=' + programme + ' and level <= ' + str(current_user.year)
                          + 'order by course.level, course.sub_session', db.engine)
    course_ids = courses['id'].values
    course_names = courses['course_name'].values

    form = SelectCourse()
    form.course_choice.choices = [(x, y) for x, y in zip(course_ids, course_names)]
    if form.validate_on_submit():
        choice = str(form.course_choice.data)
        course_info = pd.read_sql("SELECT * FROM COURSE WHERE ID = " + choice, db.engine)
        course_assessments = pd.read_sql("SELECT * FROM SUMMATIVE_ASSESSMENT where course_id = " + choice, db.engine)

        # Retrieve the latest assessment for that course
        last_assessment = (max(course_assessments['due_date'].values))
        # If the current time is after the last assessment then display after course feedback
        if time > datetime.datetime(last_assessment.year, last_assessment.month, last_assessment.day):
            student_results = pd.read_sql("SELECT CGS, NAME, SUBMITTED, CONTRIBUTION, DUE_DATE "
                                          "FROM STUDENT_SUMMATIVE_ASSESSMENTS "
                                          "INNER JOIN SUMMATIVE_ASSESSMENT "
                                          "ON STUDENT_SUMMATIVE_ASSESSMENTS.SUMMATIVE_ASSESSMENT_ID = SUMMATIVE_ASSESSMENT.ID "
                                          "WHERE STUDENT_ID = " + str(student.id) +
                                          "AND COURSE_ID = " + choice, db.engine)

            # Calculate overall grade for the course
            course_grade = 0
            for index, row in student_results.iterrows():
                course_grade = course_grade + row['cgs'] * row['contribution']

            # Get a list of the ids belongning to the logged in student's classmates
            classmates = pd.read_sql("SELECT id, username FROM student where username <> 'admin' and username <> '"
                                     + student.username + "' and year = " + str(current_user.year)
                                     + 'and programme_id =' + str(current_user.programme_id), db.engine)
            classmate_grades = []
            all_classmate_results = {}
            assessment_placements = {}
            # For each classmate get their details
            for id in classmates['id'].values:
                id = str(id)
                classmate_results = pd.read_sql("SELECT student_id, CGS, NAME, SUBMITTED, CONTRIBUTION "
                                              "FROM STUDENT_SUMMATIVE_ASSESSMENTS "
                                              "INNER JOIN SUMMATIVE_ASSESSMENT "
                                              "ON STUDENT_SUMMATIVE_ASSESSMENTS.SUMMATIVE_ASSESSMENT_ID = SUMMATIVE_ASSESSMENT.ID "
                                              "WHERE STUDENT_ID = " + id +
                                              "AND COURSE_ID = " + choice, db.engine)

                # Calculate that classmates overall grade
                grade_total = 0
                for i, row in classmate_results.iterrows():
                    grade_total = grade_total + row['cgs'] * row['contribution']
                    # Add the student's assessment result to a dictionary so rankings can be calculated
                    if row['name'] in all_classmate_results:
                        all_classmate_results[row['name']].append(row['cgs'])
                    else:
                        all_classmate_results[row['name']] = [row['cgs']]
                classmate_grades.append(grade_total)

            # Calculate the logged in student's ranking in each assessment using the binary search algorithm
            for key, value in all_classmate_results.items():
                row = student_results.loc[student_results['name'] == key]
                # bisect_right used so in the event of tied scores the student is given the best ranking instead of the worst ranking
                assessment_placements[key] = ordinal((len(value)-bisect.bisect_right(sorted(value),row['cgs'].values[0])+1))

            # Calculate the logged in student's ranking for the overall course using the binary search algorithm
            classmate_grades = (sorted(classmate_grades, key=float, reverse=False))
            # bisect_right used so in the event of tied scores the student is given the best ranking instead of the worst ranking
            course_rank = ordinal(len(classmate_grades)-bisect.bisect_right(classmate_grades,course_grade)+1)
            class_size = len(classmate_grades)+1

            # If a student places in the bottom half of the class and has more than 3 days left to submit, add a message to the list.
            poor_early_submissions = []
            for i, row in student_results.iterrows():
                if row['name'] in assessment_placements and row['name'] != "Written Exam":
                    time_left = abs(row['due_date'] - row['submitted']).days
                    ranking = int(assessment_placements[row['name']][:-2])
                    if 10 < ranking <= 20 and time_left > 3:
                        poor_early_submissions.append("You scored in the bottom half of your class for " +
                                                      row['name'] + " and submitted the assessment early " +
                                                      str(time_left) + " days early.")

            return render_template('coursefeedback.html', title='Course Feedback', form=form,
                                   course_info=course_info, course_assessments=course_assessments,
                                   student_results=student_results, course_rank=course_rank, class_size=class_size,
                                   assessment_placements=assessment_placements,
                                   poor_early_submissions=poor_early_submissions)

        #otherwise display the course in progress feedback
        else:
            student_results = pd.read_sql("SELECT CGS, NAME, SUBMITTED, CONTRIBUTION "
                                          "FROM STUDENT_SUMMATIVE_ASSESSMENTS "
                                          "INNER JOIN SUMMATIVE_ASSESSMENT "
                                          "ON STUDENT_SUMMATIVE_ASSESSMENTS.SUMMATIVE_ASSESSMENT_ID = SUMMATIVE_ASSESSMENT.ID "
                                          "WHERE STUDENT_ID = " + str(student.id) +
                                          "AND COURSE_ID = " + choice +
                                          "AND SUBMITTED <= '" +time.strftime('%Y-%m-%d') + "'", db.engine)
            current_weighted_results = []
            for index, row in student_results.iterrows():
                current_weighted_results.append(row['cgs']*row['contribution'])

            x = Symbol('x')
            # IF THIS EXCEEDS 22/A1 THEN THE STUDENT CANNOT ACHIEVE AN A5 GRADE, ADD CHECK FOR THIS
            required_grade_A5 = gradebandcheck(solve(Eq(
                sum(current_weighted_results) + (1 - sum(student_results['contribution'].values)) * x, 18),"x")[0])
            required_grade_B3 = gradebandcheck(solve(Eq(
                sum(current_weighted_results) + (1 - sum(student_results['contribution'].values)) * x, 15), "x")[0])

            return render_template('coursefeedback.html', title='Course Feedback', form=form, course_info=course_info,
                                   course_assessments=course_assessments, required_grade_A5=required_grade_A5,
                                   required_grade_B3=required_grade_B3, student_results=student_results)
    return render_template('coursefeedback.html', title='Course Feedback', form=form)


@app.route('/programmefeedback/<username>')
@login_required
def programmefeedback(username):
    student = Student.query.filter_by(username=username).first_or_404()
    # Check if the student is trying to access another student's page
    if current_user.username != student.username:
        flash('You do not have permission to view this page')
        return redirect(url_for('home'))

    student_id = str(student.id)
    student_list = pd.read_sql("SELECT id FROM student where username <> 'admin' and year = " + str(current_user.year) + 'and programme_id =' + str(current_user.programme_id), db.engine)

    level1grades = []
    level2grades = []
    all_student_level1_results = []

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
            all_student_level1_results.append(level1_results)
    #end of loop

    #logged in student's details
    level_1_scores = pd.read_sql('SELECT course.course_name as course_name, credits, '
                                 'sum(contribution * cgs) as course_grade '
                                 'from student_summative_assessments '
                                 'inner JOIN summative_assessment '
                                 'on student_summative_assessments.summative_assessment_id = summative_assessment.id '
                                 'inner JOIN course '
                                 'on summative_assessment.course_id = course.id '
                                 'inner JOIN programme_courses on course.id = programme_courses.course_id '
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
                                 'AND student_id =' + student_id + 'and course.level = 2 group by course.id', db.engine)

    total_level2_credits = level_2_scores['credits'].sum()
    student_l2_results = []

    for course_credits, grade in zip(level_2_scores['credits'].values, level_2_scores['course_grade'].values):
        student_l2_results.append(calculategpa(grade, course_credits, total_level2_credits))

    level2grade = gradebandcheck(sum(student_l2_results))
    mock_honours_grade = degreeclassification((sum(student_l1_results) * 0.3) + (sum(student_l2_results) * 0.7))
    #end of logged in student's details retrieval

    #kmeans start
    x = np.array(list(zip(level1grades, level2grades)))
    kmeans = KMeans(n_clusters=5).fit(x)

    img = io.BytesIO()
    plt.clf()
    plt.scatter(x[:, 0], x[:, 1], c=kmeans.labels_, cmap='rainbow')
    plt.plot(sum(student_l1_results),sum(student_l2_results), 'ko', label='You', markersize=7)
    plt.xlim(min(level1grades) - 1, 22)
    plt.ylim(min(level2grades) - 1, 22)
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], color='black', marker='+')#MAYBE REMOVE IN FINAL VERSION
    plt.xlabel('Level 1 Grade')
    plt.ylabel('Level 2 Grade')
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    #kmeans end

    #linear regression start
    x_training = np.array(all_student_level1_results)
    y_training = np.array(level2grades)
    x_test = np.array([student_l1_results])
    lin = linear_model.LinearRegression()
    lin.fit(x_training, y_training)
    predictedl2 = gradebandcheck(lin.predict(x_test)[0])
    testlinearregression(lin, all_student_level1_results, level2grades)
    #linear regression end

    #bayes start
    y_training=[]
    for x in level2grades:
        y_training.append(gradebandcheck(x))
    clf = GaussianNB()
    x_training = np.array(all_student_level1_results)
    x_test = np.array([student_l1_results])
    clf.fit(x_training, y_training)
    bayes_predictedl2 = (clf.predict(x_test)[0])
    testbayes(all_student_level1_results,level2grades, clf)
    #bayes end

    if predictedl2 > level2grade:
        predicted_text = "You did better than predicted, well done!"
    elif predictedl2 < level2grade:
        predicted_text = "You did worse than predicted."
    else:
        predicted_text = "You performed as predicted."

    kmeans_prediction = kmeans.predict([[sum(student_l1_results),sum(student_l2_results)]])
    if kmeans_prediction == kmeans.predict([[max(level1grades),max(level2grades)]]):
        feedback = "You are in the top performers for both year 1 and year 2, well done!"
    elif kmeans_prediction == kmeans.predict([[min(level1grades),max(level2grades)]]):
        feedback = "You have improved from year 1 and are now one of the better performers in year 2."
    elif kmeans_prediction == kmeans.predict([[min(level1grades),min(level2grades)]]):
        feedback = "You are in the worst performers for both year 1 and year 2."
    elif kmeans_prediction == kmeans.predict([[max(level1grades), min(level2grades)]]):
        feedback = "You performed well in year 1 but your results have gotten worse compared to your peers."
    else:
        feedback = "You are performing averagely compared to your peers"

    return render_template('programmefeedback.html', title='Programme Feedback', plot_url=plot_url,
                           level1grade=level1grade, level2grade=level2grade, mock_honours_grade=mock_honours_grade,
                           feedback=feedback, predictedl2=predictedl2, predicted_text=predicted_text,
                           bayes_predictedl2=bayes_predictedl2)


@app.route('/formativefeedback/<username>', methods=['GET', 'POST'])
@login_required
def formativefeedback(username):
    student = Student.query.filter_by(username=username).first_or_404()
    # Check if the student is trying to access another student's page
    if current_user.username != student.username:
        flash('You do not have permission to view this page')
        return redirect(url_for('home'))
    programme = str(student.programme_id)
    # Default values so they can be hidden on html page before user selection
    plot_url = ""
    plot_url2 = ""
    courses = pd.read_sql('select course.id, course.course_name, course.level, course.sub_session '
                          'from course inner join programme_courses on programme_courses.course_id=course.id '
                          'where programme_courses.programme_id=' + programme + ' and level <= ' + str(current_user.year)
                          + 'order by course.level, course.sub_session', db.engine)
    course_ids = courses['id'].values
    course_names = courses['course_name'].values

    form = SelectFormativeCourse()
    form.course_choice.choices = [(x, y) for x, y in zip(course_ids, course_names)]

    if form.validate_on_submit():
        choice = str(form.course_choice.data)
        start_time = form.start_dt.data
        end_time = form.end_dt.data
        df = pd.read_sql("SELECT formative_assessment.name, formative_assessment.due_date, "
                         "course.course_name, student_formative_assessments.cgs, student_formative_assessments.submitted "
                         "from formative_assessment "
                         "inner join student_formative_assessments "
                         "on student_formative_assessments.formative_assessment_id = formative_assessment.id "
                         "inner join course "
                         "on formative_assessment.course_id = course.id "
                         "where student_formative_assessments.student_id ="
                         + str(current_user.id) + "and formative_assessment.due_date >='" + start_time.strftime('%Y-%m-%d') +
                         "' and formative_assessment.due_date <='" + end_time.strftime('%Y-%m-%d') +
                         "'and course.id =" + choice +
                         " and student_formative_assessments.submitted is not NULL "
                         "order by formative_assessment.due_date", db.engine)

        if df.empty:
            flash("No results for that course.")
        else:
            objects = df['name'].values
            performance = df['cgs'].values
            x_pos = np.arange(len(objects))

            img = io.BytesIO()
            plt.clf()
            plt.bar(range(len(objects)), performance, align='center', alpha=0.5)
            plt.xticks(x_pos, objects, rotation=60)
            plt.yticks(np.arange(0, 22, 2))
            plt.ylabel('CGS Score')
            plt.title(df['course_name'].values[0] + " Results")
            plt.tight_layout()
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()

            if len(df) > 1:
                img = io.BytesIO()
                plt.clf()
                plt.plot(range(len(objects)), performance, color='black')
                classmate_ids = pd.read_sql("SELECT student_id FROM student_formative_assessments WHERE student_id <> "+str(current_user.id)+" and student_formative_assessments.submitted is not null GROUP BY student_id;", db.engine)
                for classmate_id in classmate_ids['student_id'].values:
                    classmates_results = pd.read_sql("SELECT formative_assessment.name, formative_assessment.due_date, course.course_name, student_formative_assessments.cgs, student.year "
                                                     "from formative_assessment "
                                                     "inner join student_formative_assessments "
                                                     "on student_formative_assessments.formative_assessment_id = formative_assessment.id "
                                                     "inner join course "
                                                     "on formative_assessment.course_id = course.id "
                                                     "inner join student "
                                                     "on student_formative_assessments.student_id = student.id "
                                                     "where student_formative_assessments.student_id =" + str(classmate_id) +
                                                     " and formative_assessment.due_date >='" + start_time.strftime('%Y-%m-%d') +
                                                     "' and formative_assessment.due_date <='" + end_time.strftime('%Y-%m-%d') +
                                                     " ' and course.id =" + choice +
                                                     " and student.year = " + str(current_user.year) +
                                                     " and student_formative_assessments.submitted is not NULL"
                                                     " order by formative_assessment.due_date", db.engine)
                    classmate_objects = classmates_results['name'].values
                    classmate_performance = classmates_results['cgs'].values
                    if gradebandcheck(sum(classmates_results['cgs'].values)/len(classmates_results))[0] == "A":
                        plt.plot(range(len(classmate_objects)), classmate_performance, color='pink')
                    elif gradebandcheck(sum(classmates_results['cgs'].values)/len(classmates_results))[0] == "B":
                        plt.plot(range(len(classmate_objects)), classmate_performance, color='purple')
                    elif gradebandcheck(sum(classmates_results['cgs'].values)/len(classmates_results))[0] == "C":
                        plt.plot(range(len(classmate_objects)), classmate_performance, color='blue')
                    elif gradebandcheck(sum(classmates_results['cgs'].values) / len(classmates_results))[0] == "D":
                        plt.plot(range(len(classmate_objects)), classmate_performance, color='green')
                    elif gradebandcheck(sum(classmates_results['cgs'].values) / len(classmates_results))[0] == "E":
                        plt.plot(range(len(classmate_objects)), classmate_performance, color='yellow')
                    elif gradebandcheck(sum(classmates_results['cgs'].values) / len(classmates_results))[0] == "F":
                        plt.plot(range(len(classmate_objects)), classmate_performance, color='orange')
                    else:
                        plt.plot(range(len(classmate_objects)), classmate_performance, color='red')
                plt.xticks(x_pos, objects, rotation=60)
                plt.yticks(np.arange(0, 22, 2))
                plt.ylabel('CGS Score')
                plt.title(df['course_name'].values[0] + " Results Compared to Peers")
                you_patch = mpatches.Patch(color='black', label='You')
                a_patch = mpatches.Patch(color='pink', label='A Band')
                b_patch = mpatches.Patch(color='purple', label='B Band')
                c_patch = mpatches.Patch(color='blue', label='C Band')
                d_patch = mpatches.Patch(color='green', label='D Band')
                e_patch = mpatches.Patch(color='yellow', label='E Band')
                f_patch = mpatches.Patch(color='orange', label='F Band')
                g_patch = mpatches.Patch(color='red', label='G Band')
                legend = plt.legend(loc='upper center', bbox_to_anchor=(1.1, 0.8), handles=[you_patch, a_patch, b_patch, c_patch, d_patch, e_patch, f_patch, g_patch])
                plt.tight_layout()
                plt.savefig(img, bbox_extra_artists=(legend,), bbox_inches='tight', format='png')
                img.seek(0)
                plot_url2 = base64.b64encode(img.getvalue()).decode()
            else:
                plot_url2 = ""
            scores = pd.read_sql("SELECT student_id, SUM(cgs) "
                                 "from student_Formative_assessments "
                                 "inner join student "
                                 "on student_Formative_assessments.student_id = student.id "
                                 "inner join formative_assessment "
                                 "on student_Formative_assessments.formative_assessment_id = formative_assessment.id "
                                 "where student.year =" + str(current_user.year) +
                                 " and formative_assessment.course_id = " + choice +
                                 " and formative_assessment.due_date <= '" + time.strftime('%Y-%m-%d') +
                                 "' and student_Formative_assessments.submitted is not null"
                                 " group by student_id order by sum desc", db.engine)
            position = scores.student_id[scores.student_id == current_user.id].index.tolist()[0]+1

            if position != len(scores):
                html_position = ("You are " + ordinal(position) + " out of " + str(len(scores)) + " classmates")
            else:
                html_position = ("You are last out of your " + str(len(scores)) + " classmates")
            average_grade = "Your average grade based on your formative results is " + gradebandcheck(sum(df['cgs'].values)/len(df)) + "."

            # Check how long a student had left for each submission
            time_left_messages = []
            for index, row in df.iterrows():
                time_left = abs(row['due_date']-row['submitted']).days
                cgs = row['cgs']
                #If they had more than two days left and scored a C grade or lower then add a message to the array.
                if time_left >= 2 and cgs < 15:
                    time_left_messages.append("You had " + str(time_left) + " days left before the due date for " + row['name'] + " and scored poorly, use all the time available to study the material.")

            return render_template('formative.html', title='Formative Feedback', plot_url=plot_url, plot_url2=plot_url2,
                                   form=form, html_position=html_position, average_grade=average_grade, time_left_messages=time_left_messages)
    return render_template('formative.html', title='Formative Feedback', plot_url=plot_url, plot_url2=plot_url2,
                           form=form)


@app.route('/yearfeedback/<username>', methods=['GET', 'POST'])
@login_required
def yearfeedback(username):
    student = Student.query.filter_by(username=username).first_or_404()
    # Check if the student is trying to access another student's page
    if current_user.username != student.username:
        flash('You do not have permission to view this page')
        return redirect(url_for('home'))
    if student.year > 1:
        form = SelectYear()
        if form.validate_on_submit():
            class_session1_grades = pd.DataFrame(columns=['id','grade'])
            class_session2_grades = pd.DataFrame(columns=['id','grade'])
            choice = str(form.year.data)
            # ADD CHECK TO SQL SO IT RETRIEVES SUBMITTED VALUES THAT ARE NOT NULL
            student_year_results = pd.read_sql('SELECT course.course_name as course_name, credits, sub_session, '
                                     'sum(contribution * cgs) as course_grade '
                                     'from student_summative_assessments '
                                     'inner JOIN summative_assessment '
                                     'on student_summative_assessments.summative_assessment_id = summative_assessment.id '
                                     'inner JOIN course '
                                     'on summative_assessment.course_id = course.id '
                                     'inner JOIN programme_courses on course.id = programme_courses.course_id '
                                     'AND student_id =' + str(student.id) + 'and course.level = ' + choice + ' group by course.id',
                                     db.engine)

            if student_year_results.empty:
                flash("No results for that year")
                return render_template('yearfeedback.html', title='Year Feedback', form=form)

            # Calculate logged in student's grade for sub session 1 of their selected year
            sub_session1_credits = student_year_results.loc[student_year_results['sub_session'] == 1, 'credits'].sum()
            student_session1_results = []
            for course_credits, grade in zip(student_year_results.loc[student_year_results['sub_session'] == 1, 'credits'],student_year_results.loc[student_year_results['sub_session'] == 1, 'course_grade']):
                student_session1_results.append(calculategpa(grade, course_credits, sub_session1_credits))
                sub_session1_grade = sum(student_session1_results)

            # Calculate logged in student's grade for sub session 2 of their selected year
            sub_session2_credits = student_year_results.loc[student_year_results['sub_session'] == 2, 'credits'].sum()
            student_session2_results = []
            for course_credits, grade in zip(student_year_results.loc[student_year_results['sub_session'] == 2, 'credits'],student_year_results.loc[student_year_results['sub_session'] == 2, 'course_grade']):
                student_session2_results.append(calculategpa(grade, course_credits, sub_session2_credits))
                sub_session2_grade = sum(student_session2_results)

            # Check if student has performed better or worse between the year's sub sessions
            if gradebandcheck(sub_session1_grade) == gradebandcheck(sub_session2_grade):
                sub_session_message = "Your overall performance was consistent throughout the year."
            elif sub_session1_grade < sub_session2_grade:
                sub_session_message = "Well Done, your overall performance improved throughout the year."
            else:
                sub_session_message = "Your overall performance decreased throughout the year."
            year_grade = gradebandcheck((sub_session1_grade+sub_session2_grade)/2)

            # Get each individual assessment the logged in student has completed
            all_student_assessments = pd.read_sql("select name,cgs,contribution,due_date,submitted "
                                                  "from student_summative_assessments "
                                                  "inner join summative_assessment "
                                                  "on summative_assessment.id = summative_assessment_id "
                                                  "where student_id = " + str(student.id) , db.engine)

            # Separate written exams and coursework into two lists
            written_exams = []
            coursework = []
            for index, row in all_student_assessments.iterrows():
                if row['name'] == 'Written Exam':
                    written_exams.append(row['cgs'])
                else:
                    coursework.append(row['cgs'])

            # Get a rough estimate of the student's overall performance in the two main types of assessment
            written_exam_average = gradebandcheck(sum(written_exams)/len(written_exams))
            coursework_average = gradebandcheck(sum(coursework)/len(coursework))


            # Retrieve a list of all students in the logged in student's class including themself
            class_list = pd.read_sql("SELECT id FROM student where username <> 'admin' and year = " + str(
                current_user.year) + 'and programme_id =' + str(current_user.programme_id), db.engine)

            for id in class_list['id'].values:
                id = str(id)
                year_results = pd.read_sql('SELECT course.course_name as course_name, credits, sub_session, '
                                                   'sum(contribution * cgs) as course_grade '
                                                   'from student_summative_assessments '
                                                   'inner JOIN summative_assessment '
                                                   'on student_summative_assessments.summative_assessment_id = summative_assessment.id '
                                                   'inner JOIN course '
                                                   'on summative_assessment.course_id = course.id '
                                                   'inner JOIN programme_courses on course.id = programme_courses.course_id '
                                                   'AND student_id =' + id + 'and course.level = ' + choice + ' group by course.id',db.engine)

                sub_session1_credits = year_results.loc[year_results['sub_session'] == 1, 'credits'].sum()
                session1_results = []

                for course_credits, grade in zip(
                        year_results.loc[year_results['sub_session'] == 1, 'credits'],
                        year_results.loc[year_results['sub_session'] == 1, 'course_grade']):
                    session1_results.append(calculategpa(grade, course_credits, sub_session1_credits))
                    session1_grade = sum(session1_results)

                # continue to next iteration if there are no sub session results
                if session1_grade == 0:
                    continue

                sub_session2_credits = year_results.loc[year_results['sub_session'] == 2, 'credits'].sum()
                session2_results = []

                for course_credits, grade in zip(
                        year_results.loc[year_results['sub_session'] == 2, 'credits'],
                        year_results.loc[year_results['sub_session'] == 2, 'course_grade']):
                    session2_results.append(calculategpa(grade, course_credits, sub_session2_credits))
                    session2_grade = sum(session2_results)

                if session1_grade != 0 or session2_grade != 0:
                    class_session1_grades.loc[len(class_session1_grades)] = [int(id),session1_grade]
                    class_session2_grades.loc[len(class_session2_grades)] = [int(id),session2_grade]

            # Create an array of session 1 and 2 grades for the kmeans algorithm to operate on
            x = np.array(list(zip(class_session1_grades['grade'].values, class_session2_grades['grade'].values)))

            if len(class_session1_grades) < 5:
                kmeans = KMeans(n_clusters=len(class_session1_grades)).fit(x)
            else:
                kmeans = KMeans(n_clusters=5).fit(x)

            # Plot the graph of session 1 grades against session 2 grades
            img = io.BytesIO()
            plt.clf()
            plt.scatter(x[:, 0], x[:, 1], c=kmeans.labels_, cmap='rainbow')
            plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], color='black',
                        marker='+')  # MAYBE REMOVE IN FINAL VERSION
            plt.plot(sub_session1_grade, sub_session2_grade, 'ko', label='You',markersize=7)
            plt.xlim(min(class_session1_grades['grade'].values)-1, 22)
            plt.ylim(min(class_session2_grades['grade'].values)-1, 22)
            plt.xlabel('Sub Session 1 Grade')
            plt.ylabel('Sub Session 2 Grade')
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()

            # Sort each sub session dataframe by the grade to get the position of the logged in student in relation to their peers
            class_session1_grades.sort_values(by='grade', inplace=True, ascending=False)
            class_session1_grades.reset_index(drop=True, inplace=True)
            class_session2_grades.sort_values(by='grade', inplace=True, ascending=False)
            class_session2_grades.reset_index(drop=True, inplace=True)
            sub_session1_rank = "You ranked " + ordinal(class_session1_grades.id[class_session1_grades.id == student.id].index.tolist()[0] + 1) + " out of your "  + str(len(class_list)) + " classmates for sub session 1."
            sub_session2_rank = "You ranked " + ordinal(class_session2_grades.id[class_session2_grades.id == student.id].index.tolist()[0] + 1) + " out of your "  + str(len(class_list)) + " classmates for sub session 2."

            return render_template('yearfeedback.html', title='Year ' + choice + ' Feedback', form=form,
                                   sub_session1_grade=gradebandcheck(sub_session1_grade),
                                   sub_session2_grade=gradebandcheck(sub_session2_grade),
                                   sub_session_message=sub_session_message, year_grade=year_grade, plot_url=plot_url,
                                   sub_session1_rank=sub_session1_rank, sub_session2_rank=sub_session2_rank,
                                   written_exam_average=written_exam_average, coursework_average=coursework_average)
        else:
            return render_template('yearfeedback.html', title='Year Feedback', form=form)
    else:
        class_session1_grades = pd.DataFrame(columns=['id', 'grade'])
        class_session2_grades = pd.DataFrame(columns=['id', 'grade'])
        # ADD CHECK TO SQL SO IT RETRIEVES SUBMITTED VALUES THAT ARE NOT NULL
        student_year_results = pd.read_sql('SELECT course.course_name as course_name, credits, sub_session, '
                                           'sum(contribution * cgs) as course_grade '
                                           'from student_summative_assessments '
                                           'inner JOIN summative_assessment '
                                           'on student_summative_assessments.summative_assessment_id = summative_assessment.id '
                                           'inner JOIN course '
                                           'on summative_assessment.course_id = course.id '
                                           'inner JOIN programme_courses on course.id = programme_courses.course_id '
                                           'AND student_id =' + str(
            student.id) + 'and course.level = 1 group by course.id',db.engine)

        # Calculate logged in student's grade for sub session 1 of their selected year
        sub_session1_credits = student_year_results.loc[student_year_results['sub_session'] == 1, 'credits'].sum()
        student_session1_results = []
        for course_credits, grade in zip(
                student_year_results.loc[student_year_results['sub_session'] == 1, 'credits'],
                student_year_results.loc[student_year_results['sub_session'] == 1, 'course_grade']):
            student_session1_results.append(calculategpa(grade, course_credits, sub_session1_credits))
            sub_session1_grade = sum(student_session1_results)

        # Calculate logged in student's grade for sub session 2 of their selected year
        sub_session2_credits = student_year_results.loc[student_year_results['sub_session'] == 2, 'credits'].sum()
        student_session2_results = []
        for course_credits, grade in zip(
                student_year_results.loc[student_year_results['sub_session'] == 2, 'credits'],
                student_year_results.loc[student_year_results['sub_session'] == 2, 'course_grade']):
            student_session2_results.append(calculategpa(grade, course_credits, sub_session2_credits))
            sub_session2_grade = sum(student_session2_results)

        # Check if student has performed better or worse between the year's sub sessions
        if gradebandcheck(sub_session1_grade) == gradebandcheck(sub_session2_grade):
            sub_session_message = "Your overall performance was consistent throughout the year."
        elif sub_session1_grade < sub_session2_grade:
            sub_session_message = "Well Done, your overall performance improved throughout the year."
        else:
            sub_session_message = "Your overall performance decreased throughout the year."
        year_grade = "With these results your overall grade for the year is: " + gradebandcheck(
            (sub_session1_grade + sub_session2_grade) / 2)

        # Get each individual assessment the logged in student has completed
        all_student_assessments = pd.read_sql("select name,cgs,contribution,due_date,submitted "
                                              "from student_summative_assessments "
                                              "inner join summative_assessment "
                                              "on summative_assessment.id = summative_assessment_id "
                                              "where student_id = " + str(student.id), db.engine)

        # Separate written exams and coursework into two lists
        written_exams = []
        coursework = []
        for index, row in all_student_assessments.iterrows():
            if row['name'] == 'Written Exam':
                written_exams.append(row['cgs'])
            else:
                coursework.append(row['cgs'])

        # Get a rough estimate of the student's overall performance in the two main types of assessment
        written_exam_average = gradebandcheck(sum(written_exams) / len(written_exams))
        coursework_average = gradebandcheck(sum(coursework) / len(coursework))

        # Retrieve a list of all students in the logged in student's class including themself
        class_list = pd.read_sql("SELECT id FROM student where username <> 'admin' and year = " + str(
            current_user.year) + 'and programme_id =' + str(current_user.programme_id), db.engine)

        for id in class_list['id'].values:
            id = str(id)
            year_results = pd.read_sql('SELECT course.course_name as course_name, credits, sub_session, level, '
                                       'sum(contribution * cgs) as course_grade '
                                       'from student_summative_assessments '
                                       'inner JOIN summative_assessment '
                                       'on student_summative_assessments.summative_assessment_id = summative_assessment.id '
                                       'inner JOIN course '
                                       'on summative_assessment.course_id = course.id '
                                       'inner JOIN programme_courses on course.id = programme_courses.course_id '
                                       'AND student_id =' + id + 'and course.level = 1 group by course.id',
                                       db.engine)

            sub_session1_credits = year_results.loc[year_results['sub_session'] == 1, 'credits'].sum()
            session1_results = []

            for course_credits, grade in zip(
                    year_results.loc[year_results['sub_session'] == 1, 'credits'],
                    year_results.loc[year_results['sub_session'] == 1, 'course_grade']):
                session1_results.append(calculategpa(grade, course_credits, sub_session1_credits))
                session1_grade = sum(session1_results)

            # continue to next iteration if there are no sub session results
            if session1_grade == 0:
                continue

            sub_session2_credits = year_results.loc[year_results['sub_session'] == 2, 'credits'].sum()
            session2_results = []

            for course_credits, grade in zip(
                    year_results.loc[year_results['sub_session'] == 2, 'credits'],
                    year_results.loc[year_results['sub_session'] == 2, 'course_grade']):
                session2_results.append(calculategpa(grade, course_credits, sub_session2_credits))
                session2_grade = sum(session2_results)

            if session1_grade != 0 or session2_grade != 0:
                class_session1_grades.loc[len(class_session1_grades)] = [int(id), session1_grade]
                class_session2_grades.loc[len(class_session2_grades)] = [int(id), session2_grade]

            year1_credits = year_results.loc[year_results['level'] == 1, 'credits'].sum()
            student_year1_results = []
            for course_credits, grade in zip(
                    year_results.loc[year_results['level'] == 1, 'credits'],
                    year_results.loc[year_results['level'] == 1, 'course_grade']):
                student_year1_results.append(calculategpa(grade, course_credits, year1_credits))

        # Create an array of session 1 and 2 grades for the kmeans algorithm to operate on
        x = np.array(list(zip(class_session1_grades['grade'].values, class_session2_grades['grade'].values)))
        if len(class_session1_grades) < 5:
            kmeans = KMeans(n_clusters=len(class_session1_grades)).fit(x)
        else:
            kmeans = KMeans(n_clusters=5).fit(x)
        img = io.BytesIO()
        plt.clf()
        plt.plot(sub_session1_grade, sub_session2_grade, 'ko', label='You', markersize=7)
        plt.scatter(x[:, 0], x[:, 1], c=kmeans.labels_, cmap='rainbow')
        plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], color='black',
                    marker='+')  # MAYBE REMOVE IN FINAL VERSION
        plt.xlim(min(class_session1_grades['grade'].values) - 1, 22)
        plt.ylim(min(class_session2_grades['grade'].values) - 1, 22)
        plt.xlabel('Sub Session 1 Grade')
        plt.ylabel('Sub Session 2 Grade')
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        # Sort each sub session dataframe by the grade to get the position of the logged in student in relation to their peers
        class_session1_grades.sort_values(by='grade', inplace=True, ascending=False)
        class_session1_grades.reset_index(drop=True, inplace=True)
        class_session2_grades.sort_values(by='grade', inplace=True, ascending=False)
        class_session2_grades.reset_index(drop=True, inplace=True)
        sub_session1_rank = "You ranked " + ordinal(class_session1_grades.id[class_session1_grades.id == student.id].index.tolist()[0] + 1) + " out of your "  + str(len(class_list)) + " classmates for sub session 1."
        sub_session2_rank = "You ranked " + ordinal(class_session2_grades.id[class_session2_grades.id == student.id].index.tolist()[0] + 1) + " out of your "  + str(len(class_list)) + " classmates for sub session 2."

        # Retrieve a list of all students who have already completed level 1 of the degree programme
        past_student_list = pd.read_sql("SELECT id, username FROM student where username <> 'admin' and year > " + str(
            current_user.year) + 'and programme_id =' + str(current_user.programme_id), db.engine)
        past_student_year1_results = []
        past_student_year2_grades = []

        # Get the ids of the all the students who are in later years than the currently logged in student.
        for id in past_student_list['id'].values:
            id = str(id)
            year1_and_year2_results = pd.read_sql('SELECT course.course_name as course_name, credits, sub_session, level, '
                                       'sum(contribution * cgs) as course_grade '
                                       'from student_summative_assessments '
                                       'inner JOIN summative_assessment '
                                       'on student_summative_assessments.summative_assessment_id = summative_assessment.id '
                                       'inner JOIN course '
                                       'on summative_assessment.course_id = course.id '
                                       'inner JOIN programme_courses on course.id = programme_courses.course_id '
                                       'AND student_id =' + id + 'and course.level < 3 group by course.id',
                                       db.engine)

            year1_credits = year1_and_year2_results.loc[year1_and_year2_results['level'] == 1, 'credits'].sum()
            year1_results = []
            for course_credits, grade in zip(
                    year1_and_year2_results.loc[year1_and_year2_results['level'] == 1, 'credits'],
                    year1_and_year2_results.loc[year1_and_year2_results['level'] == 1, 'course_grade']):
                year1_results.append(calculategpa(grade, course_credits, year1_credits))
                year1_grade = sum(year1_results)

            year2_credits = year1_and_year2_results.loc[year1_and_year2_results['level'] == 2, 'credits'].sum()
            year2_results = []

            for course_credits, grade in zip(
                    year1_and_year2_results.loc[year1_and_year2_results['level'] == 2, 'credits'],
                    year1_and_year2_results.loc[year1_and_year2_results['level'] == 2, 'course_grade']):
                year2_results.append(calculategpa(grade, course_credits, year2_credits))
                year2_grade = sum(year2_results)

            if year1_grade != 0 or year2_grade != 0:
                past_student_year1_results.append(year1_results)
                past_student_year2_grades.append(gradebandcheck(year2_grade))

        # Train gaussian bayes and make prediction for the logged in student
        x_training = np.array(past_student_year1_results)
        y_training = np.array(past_student_year2_grades)
        clf = GaussianNB()
        x_test = np.array([student_year1_results])
        clf.fit(x_training, y_training)
        bayes_prediction = (clf.predict(x_test)[0])

        return render_template('yearfeedback.html', title='Year 1 Feedback',
                               sub_session2_grade=gradebandcheck(sub_session2_grade),
                               sub_session_message=sub_session_message, year_grade=year_grade, plot_url=plot_url,
                               sub_session1_rank=sub_session1_rank, sub_session2_rank=sub_session2_rank,
                               prediction=bayes_prediction,written_exam_average=written_exam_average,
                               coursework_average=coursework_average)


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
                          dob=form.dob.data, programme_id=form.programme_id.data, year=form.year.data)
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
                    if str(form.submitted.data) == 'None':
                        db.engine.execute(text(
                            'INSERT INTO student_formative_assessments (student_id, formative_assessment_id, cgs, submitted) VALUES (' + student_id + ',' + formative_assessment_id + ',' + str(
                                form.cgs.data) + ', NUll)'))
                    else:
                        db.engine.execute(text(
                            'INSERT INTO student_formative_assessments (student_id, formative_assessment_id, cgs, submitted) VALUES (' + student_id + ',' + formative_assessment_id + ',' + str(
                                form.cgs.data) + ",'" + str(form.submitted.data) + "')"))

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
                            form.cgs.data)  + ",'" + str(form.submitted.data) + "')"))
                    flash('Result added')
                    break
                else:
                    flash('User is not enrolled on that course')
        return redirect(url_for('addsummativeresult'))
    return render_template('admin/addsummativeresult.html', title='Add Summative Result', form=form)
