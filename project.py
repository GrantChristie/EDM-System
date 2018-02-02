from app import app, db
from app.models import User


# Setup for 'flask shell' command
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}
