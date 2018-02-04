import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Setup database connections
    SQLALCHEMY_DATABASE_URI = 'postgres://hjzkziifziiquf:6eb33839b47aee5cdfb2fe05b676b12a43c356d58ffe8eb50599062d32c88c6c@ec2-54-227-244-122.compute-1.amazonaws.com:5432/d840j638usekgp' or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
