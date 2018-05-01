from app import db, login
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

# Model for programme - course association table
programme_courses = db.Table('programme_courses',
                             db.Column("id", db.Integer,
                                       primary_key=True,
                                       autoincrement=True),
                             db.Column('programme_id',
                                       db.Integer,
                                       db.ForeignKey("programme.id")),
                             db.Column('course_id',
                                       db.Integer,
                                       db.ForeignKey("course.id"))
                             )

# Model for student - formative assessment association table
student_formative_assessments = db.Table('student_formative_assessments',
                                         db.Column("id", db.Integer,
                                                   primary_key=True,
                                                   autoincrement=True),
                                         db.Column('student_id', db.Integer,
                                                   db.ForeignKey("student.id")),
                                         db.Column('formative_assessment_id',
                                                   db.Integer,
                                                   db.ForeignKey("formative_assessment.id")),
                                         db.Column('cgs', db.Integer),
                                         db.Column('submitted', db.Date)
                                         )

# Model for student - summative assessment association table
student_summative_assessments = db.Table('student_summative_assessments',
                                         db.Column("id", db.Integer,
                                                   primary_key=True,
                                                   autoincrement=True),
                                         db.Column('student_id', db.Integer,
                                                   db.ForeignKey("student.id")),
                                         db.Column('summative_assessment_id',
                                                   db.Integer,
                                                   db.ForeignKey("summative_assessment.id")),
                                         db.Column('cgs', db.Integer),
                                         db.Column('submitted', db.Date)
                                         )


# Model for student table
class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    f_name = db.Column(db.String(40))
    l_name = db.Column(db.String(40))
    dob = db.Column(db.Date)
    year = db.Column(db.Integer)
    attendance = db.Column(db.Float)
    programme_id = db.Column(db.Integer, db.ForeignKey('programme.id'))
    student_formative_assessments = db.relationship('FormativeAssessment',
                                                    secondary=student_formative_assessments,
                                                    backref=db.backref("students",
                                                                       lazy="dynamic"),
                                                    )

    student_summative_assessments = db.relationship('SummativeAssessment',
                                                    secondary=student_summative_assessments,
                                                    backref=db.backref("students",
                                                                       lazy="dynamic"),
                                                    )

    def __repr__(self):
        return '<Student {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Model for programme table
class Programme(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    programme_name = db.Column(db.String(40), unique=True)
    students = db.relationship('Student', backref='student', lazy='dynamic')
    programme_courses = db.relationship('Course',
                                        secondary=programme_courses,
                                        backref=db.backref("programmes",
                                                           lazy="dynamic"),
                                        )

    def __repr__(self):
        return '<Programme {}>'.format(self.programme_name)


# Model for course table
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(128))
    level = db.Column(db.Integer)
    credits = db.Column(db.Integer)
    sub_session = db.Column(db.Integer)
    formative_assessments = db.relationship('FormativeAssessment',
                                            backref='formative_assessment',
                                            lazy='dynamic')
    summative_assessments = db.relationship('SummativeAssessment',
                                            backref='summative_assessment',
                                            lazy='dynamic')

    def __repr__(self):
        return '<Course {}>'.format(self.course_name)


# Model for summative assessment table
class SummativeAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40))
    due_date = db.Column(db.Date)
    contribution = db.Column(db.Float)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    academic_excellence = db.Column(db.Integer)
    critical_thinking = db.Column(db.Integer)
    learning_personal_development = db.Column(db.Integer)
    active_citizenship = db.Column(db.Integer)

    def __repr__(self):
        return '<Summative Assessment {}>'.format(self.name)


# Model for formative assessment table
class FormativeAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40))
    due_date = db.Column(db.Date)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __repr__(self):
        return '<Formative Assessment {}>'.format(self.name)


# Retrives ID of student from the current session
@login.user_loader
def load_user(id):
    return Student.query.get(int(id))
