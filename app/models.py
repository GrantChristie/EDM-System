from app import db, login
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin


class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    f_name = db.Column(db.String(40))
    l_name = db.Column(db.String(40))
    DOB = db.Column(db.Date)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Retrives ID of student from the current session
@login.user_loader
def load_user(id):
    return Student.query.get(int(id))