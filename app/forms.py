from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, NumberRange
from wtforms.fields.html5 import DateField, IntegerField
import datetime


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class AddStudent(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    f_name = StringField('First Name', validators=[DataRequired()])
    l_name = StringField('Last Name', validators=[DataRequired()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    programme_id = SelectField('Programme', coerce=int)
    submit = SubmitField('Add')


class AddProgramme(FlaskForm):
    programme_name = StringField('Programme Name', validators=[DataRequired()])
    submit = SubmitField('Add')


class AddCourse(FlaskForm):
    course_name = StringField('Course Name', validators=[DataRequired()])
    level = IntegerField('Course Level', default=1, validators=[DataRequired()])
    credits = IntegerField('Course Credits', default=15, validators=[DataRequired()])
    submit = SubmitField('Add')


class AddFormativeAssessment(FlaskForm):
    name = StringField('Assessment Name', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()], default=datetime.datetime.now())
    course_id = SelectField('Course', coerce=int)
    submit = SubmitField('Add')


class AddSummativeAssessment(FlaskForm):
    name = StringField('Assessment Name', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()], default=datetime.datetime.now())
    contribution = FloatField('Grade Contribution', validators=[DataRequired()], default=0.75)
    course_id = SelectField('Course', coerce=int)
    submit = SubmitField('Add')


class AddCourseToProgramme(FlaskForm):
    course_id = SelectField('Course', coerce=int)
    programme_id = SelectField('Programme', coerce=int)
    submit = SubmitField('Add')


class AddFormativeResult(FlaskForm):
    student_id = SelectField('Student', coerce=int)
    formative_assessment_id = SelectField('Formative Assessment', coerce=int)
    cgs = IntegerField('CGS', default=0, validators=[NumberRange(min=0, max=22)])
    submitted = SelectField('Submitted', choices=[(1, 'Yes'), (0, 'No')], coerce=int)
    submit = SubmitField('Add')


class AddSummativeResult(FlaskForm):
    student_id = SelectField('Student', coerce=int)
    summative_assessment_id = SelectField('Summative Assessment', coerce=int)
    cgs = IntegerField('CGS', default=0, validators=[NumberRange(min=0, max=22)])
    submitted = SelectField('Submitted', choices=[(1, 'Yes'), (0, 'No')], coerce=int)
    submit = SubmitField('Add')


class SelectCourse(FlaskForm):
    dt = DateField('Select Date', format='%Y-%m-%d', default=datetime.datetime.now())
    course_choice = SelectField('Choose a course', coerce=int)
    submit = SubmitField('Select')
