import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Setup database connections
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') \
                              or 'postgres://postgres:root@localhost:5432/app'
    #Undo the below comment if you want to access the heroku database from a local version of the application
    #SQLALCHEMY_DATABASE_URI = 'postgres://fhwcwrcqdyeqsy:68e08b2687bf89bfe87b7625e7c5fccaad9c5c40f60a2bb9d56d345a731ee2f2@ec2-54-235-64-195.compute-1.amazonaws.com:5432/d47qfbn739u0oe'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
