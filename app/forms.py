from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddUser(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    attendance = IntegerField('Attendance', validators=[DataRequired()])
    score = IntegerField('Score', validators=[DataRequired()])
    submit = SubmitField('Add')

class AddInfo(FlaskForm):
    attendance = IntegerField('Attendance', validators=[DataRequired()])
    score = IntegerField('Score', validators=[DataRequired()])
    submit = SubmitField('Get Feedback!')