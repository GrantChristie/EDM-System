from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, FloatField
from wtforms.validators import DataRequired


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
    submit = SubmitField('Add')

class AddFormativeAssessment(FlaskForm):
    name = StringField('Assessment Name', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int)
    submit = SubmitField('Add')

class AddSummativeAssessment(FlaskForm):
    name = StringField('Assessment Name', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    contribution = FloatField('Grade Contribution', validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int)
    submit = SubmitField('Add')
