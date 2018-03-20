import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Setup database connections
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') \
                              or 'postgres://postgres:root@localhost:5432/app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
