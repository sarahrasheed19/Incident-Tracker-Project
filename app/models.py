from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db
import datetime

#table for the foreign key relationship
#Incident_User = db.Table('Incident_User',
  #  db.Column('user_id', db.Integer(), db.ForeignKey('User.id')),
  #  db.Column('incident_id', db.Integer(), db.ForeignKey('Incident.incidentID'))
  #  )

#User class
class User(UserMixin, db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    #changed password length from 30 to 100 due to passwords being hashed
    password = db.Column(db.String(100), nullable=False)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    userType = db.Column(db.String(20), nullable=False)
    incident_created = db.Column(db.Integer, db.ForeignKey('Incident.incidentID'), nullable=True)
    incident_assigned = db.Column(db.Integer, db.ForeignKey('Incident.incidentID'), nullable=True)
    #broke up the relationship line into two, each holding one foreign key in the list as opposed to two foreign keys
    #also going to assume that the incident table needs the same change.
    #should resolve the ambiguousforeignkeyserror
    incidents_created = db.relationship('Incident', backref='user', lazy=True, foreign_keys=[incident_created])
    incidents_assigned = db.relationship('Incident', lazy=True, foreign_keys=[incident_assigned])
    #nullable =True because not everyone has to be assigned an incident to handle
    #incident_assigned = db.Column(db.Integer, db.ForeignKey('Incident.incidentID'), nullable=True)
    #figuring out how foreign keys are gonna work

    def __repr__(self):
        return f"User('{self.fname}', '{self.username}', '{self.email}')"

    def __init__(self, username, email, password, fname, lname, userType, incident_created, incident_assigned):
        self.username = username
        self.email = email
        self.password = password
        self.fname = fname
        self.lname = lname
        self.userType = userType
        self.incident_created = incident_created
        self.incident_assigned = incident_assigned

#Incident class
class Incident(db.Model):
    __tablename__ = 'Incident'

    incidentID = db.Column(db.Integer, primary_key=True)
    #added title column
    title = db.Column(db.String(40), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    date_resolved = db.Column(db.DateTime, nullable=True)
    state = db.Column(db.String(20), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    #treating case_history like a description for now
    case_history = db.Column(db.String(150), nullable=False)
    #explicit relationship, backreferences the table User, lazy = loads all necessary data
    #at once, just has to do with queries
    assignee = db.Column(db.Integer, db.ForeignKey('User.incident_assigned'),nullable=True)
    point_of_contact = db.Column(db.Integer, db.ForeignKey('User.incident_created'),nullable=False)
    #broke up the relationship line into two
    users_assignee = db.relationship('User', backref='incident', lazy=True, foreign_keys=[point_of_contact])
    users_poc = db.relationship('User', lazy=True, foreign_keys=[assignee])
    #point_of_contact = db.Column(db.Integer, db.ForeignKey('User.id'),nullable=False)
    #current_assignee = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #figuring out how foreign keys are gonna work

    def __repr__(self):
        return f"Ticket #{self.incidentID} created by {self.point_of_contact}"

    def __init__(self, title, category, description, date_created, date_resolved, state, tag, case_history, assignee, point_of_contact):
        self.title = title
        self.category = category
        self.description = description
        self.date_created = date_created
        self.date_resolved = date_resolved
        self.state = state
        self.tag = tag
        self.case_history = case_history
        self.assignee = assignee
        self.point_of_contact = point_of_contact

#Incident_History class
class Incident_History(db.Model):
    __tablename__ = 'Incident_History'

    incident_history_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    incident_id = db.Column(db.Integer, db.ForeignKey('Incident.incidentID'), nullable=False)
    incident_history = db.Column(db.String(500), nullable=True)
    users = db.relationship('User', backref='Incident', lazy=True, foreign_keys=[user_id])
    incidents = db.relationship('Incident', backref='User', lazy=True, foreign_keys=[incident_id, incident_history])

    def __repr__(self):
        return f"Ticket history: {self.incident_history} created by {self.user_id}. Incident ID: {self.incident_id}."

    def __init__(self, user_id, incident_id, incident_history):
        self.user_id = user_id
        self.incident_id = incident_id
        self.incident_history = incident_history
