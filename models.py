from extensions import db
from flask_login import UserMixin

class user(db.Model,UserMixin):
    __tablename__ = 'user'
    uid = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.Text,unique=True, nullable=True)
    password  = db.Column(db.Text)
    email = db.Column(db.Text,nullable=True,unique=True)
    
    skills = db.relationship('Skill', backref='user' ,cascade="all,delete", lazy=True)
    education = db.relationship('Education', backref='user',cascade="all,delete", lazy=True)
    projects = db.relationship('Project', backref='user',cascade="all,delete", lazy=True)
    links = db.relationship('Link', backref='user',cascade="all,delete", lazy=True)
    user_detail = db.relationship('Detail', backref='user',cascade="all,delete", lazy=True)
    def get_id(self):
        return str(self.uid)
  


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Text, db.ForeignKey('user.username',ondelete='CASCADE'), nullable=False)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    degree = db.Column(db.String(100))
    institution = db.Column(db.String(100))
    year = db.Column(db.String(10))
    user_id = db.Column(db.Text, db.ForeignKey('user.username',ondelete='CASCADE'), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    user_id = db.Column(db.Text, db.ForeignKey('user.username',ondelete='CASCADE'), nullable=False)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))  # e.g., GitHub, LinkedIn
    url = db.Column(db.String(200))
    user_id = db.Column(db.Text, db.ForeignKey('user.username',ondelete='CASCADE'), nullable=False)

class Detail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200))  # store the URL or file path
    name = db.Column(db.String(200)) 
    date_of_birth = db.Column(db.Text) 
    prof  = db.Column(db.String(90)) 
    description = db.Column(db.String(2000)) 
    user_id = db.Column(db.Text, db.ForeignKey('user.username',ondelete='CASCADE'), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    location=db.Column(db.String(200))
