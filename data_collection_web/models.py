from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from data_collection_web import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20)) 
    password_hash = db.Column(db.String(128)) 

    def set_password(self, password):  
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):  
        return check_password_hash(self.password_hash, password) 

class Reaction(db.Model):
    __tablename__ = 'reaction'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10000), nullable=False)
    steps = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', primaryjoin='Reaction.user_id == User.id')