from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#The above will give the user_id stored in database

 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Posti', backref='author', lazy=True)
    ''' Author is backreference which helps to get entire info of user and its attributes###
    why we use 'backref', 'relationship'-->more on 
    https://hackingandslacking.com/managing-relationships-in-sqlalchemy-data-models-effe9d1c8975'''

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Posti(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Posti('{self.title}', '{self.date_posted}')"




