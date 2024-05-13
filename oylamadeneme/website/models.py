from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import json



class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

class Poll(db.Model):
    __tablename__ = 'polls'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(250), nullable=False)
    options = db.Column(db.Text, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    def set_options(self, options):  # JSON verilerini kaydetmek için özel bir metot
        self.options = json.dumps(options)

    def get_options(self):  # JSON verilerini çekmek için özel bir metot
        return json.loads(self.options)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    choice = db.Column(db.Boolean, nullable=False)  # True for yes, False for no

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    votes = db.relationship('Vote', backref='voter', lazy=True)
    groups = db.relationship('Group', secondary='user_group', backref='users')
    
def get_user_votes(user_id):
        return Vote.query.filter_by(user_id=user_id).all()

def get_user_groups(user_id):
    user_groups = Member.query.filter_by(user_id=user_id).all()
    groups = [group.group for group in user_groups]
    return groups

user_group = db.Table('user_group',  #Kullanıcıların gruplara üyeliklerini tutmak için. 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)