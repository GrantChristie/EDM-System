from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, \
    FloatField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms.fields.html5 import DateField, IntegerField
import datetime


# Form displayed on /login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Form displayed on /addstudent
class AddStudent(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    f_name = StringField('First Name', validators=[DataRequired()])
    l_name = StringField('Last Name', validators=[DataRequired()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    year = IntegerField('Student Year', validators=[DataRequired()],
                        default=1)
    attendance = FloatField('Attendance', validators=[DataRequired()],
                            default=1)
    programme_id = SelectField('Programme', coerce=int)
    submit = SubmitField('Add')


# Form displayed on /addprogramme
class AddProgramme(FlaskForm):
    programme_name = StringField('Programme Name', validators=[DataRequired()])
    submit = SubmitField('Add')


# Form displayed on /addcourse
class AddCourse(FlaskForm):
    course_name = StringField('Course Name', validators=[DataRequired()])
    level = IntegerField('Course Level', default=1,
                         validators=[DataRequired()])
    credits = IntegerField('Course Credits', default=15,
                           validators=[DataRequired()])
    submit = SubmitField('Add')


# Form displayed on /addformativeassessment
class AddFormativeAssessment(FlaskForm):
    name = StringField('Assessment Name', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()],
                         default=datetime.datetime.now())
    course_id = SelectField('Course', coerce=int)
    submit = SubmitField('Add')


# Form displayed on /addsummativeassessment
class AddSummativeAssessment(FlaskForm):
    name = StringField('Assessment Name', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()],
                         default=datetime.datetime.now())
    contribution = FloatField('Grade Contribution',
                              validators=[DataRequired()],
                              default=0.75)
    academic_excellence = SelectField('Academic Excellence',
                                      choices=[(1, '1'), (0, '0')],
                                      coerce=int)
    active_citizenship = SelectField('Active Citizenship',
                                     choices=[(1, '1'), (0, '0')],
                                     coerce=int)
    critical_thinking = SelectField('Critical Thinking',
                                    choices=[(1, '1'), (0, '0')],
                                    coerce=int)
    learning_personal_development = SelectField('Learning and Personal Development',
                                                choices=[(1, '1'), (0, '0')],
                                                coerce=int)
    course_id = SelectField('Course', coerce=int)
    submit = SubmitField('Add')


# Form displayed on /addcoursetoprogramme
class AddCourseToProgramme(FlaskForm):
    course_id = SelectField('Course', coerce=int)
    programme_id = SelectField('Programme', coerce=int)
    submit = SubmitField('Add')


# Form displayed on /addformativeresult
class AddFormativeResult(FlaskForm):
    student_id = SelectField('Student', coerce=int)
    formative_assessment_id = SelectField('Formative Assessment', coerce=int)
    cgs = IntegerField('CGS', default=0,
                       validators=[NumberRange(min=0, max=22)])
    submitted = DateField('Date Submitted On', validators=[Optional()])
    submit = SubmitField('Add')


# Form displayed on /addsummativeresult
class AddSummativeResult(FlaskForm):
    student_id = SelectField('Student', coerce=int)
    summative_assessment_id = SelectField('Summative Assessment', coerce=int)
    cgs = IntegerField('CGS', default=0,
                       validators=[NumberRange(min=0, max=22)])
    submitted = DateField('Date Submitted On', validators=[Optional()])
    submit = SubmitField('Add')


# Form displayed on /formativefeedback
class SelectFormativeCourse(FlaskForm):
    start_dt = DateField('Select Start Date', format='%Y-%m-%d',
                         default=datetime.datetime.now())
    end_dt = DateField('Select End Date', format='%Y-%m-%d',
                       default=datetime.datetime.now())
    course_choice = SelectField('Choose a course', coerce=int)
    submit = SubmitField('Select')


# Form displayed on /yearfeedback
class SelectYear(FlaskForm):
    year = SelectField('Choose a year to get feedback for',
                       choices=[(1, '1'), (2, '2')], coerce=int)
    submit = SubmitField('Select')


# Form displayed on /coursefeedback
class SelectCourse(FlaskForm):
    course_choice = SelectField('Choose a course', coerce=int)
    submit = SubmitField('Select')
