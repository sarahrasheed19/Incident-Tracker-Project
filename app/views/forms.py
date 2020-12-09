from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import InputRequired, Length
from app.models import Incident, User, Incident_History
from app.extensions import db
from datetime import datetime

#creating blueprint
blueprint = Blueprint("forms", __name__)

#making a list of tags
tagNames = ['', 'Account Request', 'Equipment', 'File Issue', 'Hardware Issue', 'Information Security', 'Inventory', 'Network Issue', 'New Hire', 'Password Reset', 'PC Allocation', 'Purchase Request',
'Software Installation', 'Software Issue']

categories = ['Low', 'Medium', 'High']

statuses = ['Open', 'In Progress', 'On Hold', 'Awaiting Callback', 'Closed']

@blueprint.route('/create-incident')
def create_incident():
    users = User.query.all()
    names = []
    for user in users:
        name = str(user.fname + " " + user.lname)
        names.append(name)

    return render_template('forms/create_incident.html', categories = categories, users = names, tagNames = tagNames)

#create incident route
@login_required
@blueprint.route('/created-incident', methods = ['GET', 'POST'])
def created_incident():
    form = request.form

    users = User.query.all()
    for user in users:
        if form["poc"] == str(user.fname + " " + user.lname):
            pocID = user.id
        if form["assignee"] == str(user.fname + " " + user.lname):
            assigneeID = user.id

    newIncident = Incident(title = form["title"],
                          category = form["category"],
                          description = form["description"],
                          date_created = datetime.now().strftime('%Y-%m-%d %I:%M'),
                          date_resolved = None,
                          state = "Open",
                          tag = str(form["tag1"] + ", " + form["tag2"] + ", " + form["tag3"]),
                          case_history = str("Ticket created on " + str(datetime.now().strftime('%Y-%m-%d %I:%M'))),
                          assignee = assigneeID,
                          point_of_contact = pocID)

    db.session.add(newIncident)
    db.session.commit()

    newIncidentHistory = Incident_History(user_id = pocID, incident_id = newIncident.incidentID, incident_history = newIncident.case_history)
    db.session.add(newIncidentHistory)
    db.session.commit()

    return redirect(url_for('home.dashboard'))

#edit ticket route
@login_required
@blueprint.route('/edit/<int:ticketID>')
def edit_incident(ticketID):
    incident = Incident.query.get(ticketID)

    users = User.query.all()
    names = []

    POC = ''
    currentAssignee = ''

    for user in users:
        name = str(user.fname + " " + user.lname)
        names.append(name)
        if incident.point_of_contact == user.id:
            POC = str(user.fname + " " + user.lname)

        if incident.assignee == user.id:
            currentAssignee = str(user.fname + " " + user.lname)

    currentTags = incident.tag.split(', ')

    return render_template('forms/edit_incident.html', incident = incident, users = names, categories = categories, tagNames = tagNames, currentTags = currentTags, POC = POC, currentAssignee = currentAssignee)

#edited ticket route
@login_required
@blueprint.route('/edit/<int:ticketID>', methods=["GET", "POST"])
def edited_incident(ticketID):
    form = request.form

    incident = Incident.query.get(ticketID)

    if incident.title != form["title"] and form["title"] != '':
        incident.title = form["title"]
    if incident.category != form["category"] and form["category"] != '':
        incident.category = form["category"]
    if incident.description != form["description"] and form["description"] != '':
        incident.description = form["description"]

    assignedUser = User.query.get(incident.assignee)
    assignedUserName = str(assignedUser.fname + " " + assignedUser.lname)

    poc = User.query.get(incident.point_of_contact)
    pocName = str(poc.fname + " " + poc.lname)

    if assignedUserName != form["assignee"] and form["assignee"] != '':
        for user in User.query.all():
            if form["assignee"] == str(user.fname + " " + user.lname):
                incident.assignee = user.id

    if pocName != form["poc"] and form["poc"] != '':
        for user in User.query.all():
            if form["poc"] == str(user.fname + " " + user.lname):
                incident.point_of_contact = user.id

    individualTags = incident.tag.split(', ')
    if len(individualTags) == 1 and form["tag2"] != '':
        incident.tag = str(incident.tag + ", " + form["tag2"])
        if form["tag3"] != '':
            incident.tag = str(incident.tag + ", " + form["tag2"] + ", " + form["tag3"])

    if len(individualTags) == 2 and form["tag3"] != '':
        incident.tag = str(incident.tag + ", " + form["tag3"])

    for i in individualTags:
        if i != form["tag1"] and form["tag1"] != '':
            incident.tag.replace(i, form["tag1"])
        if i != form["tag2"] and form["tag2"] != '':
            incident.tag.replace(i, form["tag2"])
        if i != form["tag3"] and form["tag3"] != '':
            incident.tag.replace(i, form["tag3"])

    db.session.commit()
    return redirect(url_for('home.dashboard'))

#update ticket
@login_required
@blueprint.route('/update/<int:ticketID>', methods = ["GET", "POST"])
def update_incident(ticketID):
    form = request.form

    incident = Incident.query.get(ticketID)

    currentState = incident.state

    caseHistory = str("Ticket updated on " + datetime.now().strftime('%Y-%m-%d %I:%M'))

    if request.method == 'POST':
        if form["desc"] != '':
            caseHistory = str(caseHistory + "\n Message added by " + current_user.fname + " " + current_user.lname + ": " + form["desc"])
        if form["state"] != '':
            caseHistory = str(caseHistory + "\n Status updated by " + current_user.fname + " " + current_user.lname + " to: " + form["state"])
            incident.state = form["state"]
            if form["state"] == "Closed":
                incident.date_resolved = datetime.now().strftime('%Y-%m-%d %I:%M')
                caseHistory = str(caseHistory + "\n Ticket closed by " + current_user.fname + " " + current_user.lname + " on " + datetime.now().strftime('%Y-%m-%d %I:%M'))

        newIncidentHistory = Incident_History(user_id = current_user.id, incident_id = ticketID, incident_history = caseHistory)
        db.session.add(newIncidentHistory)
        db.session.commit()
        return redirect(url_for('home.dashboard'))

    return render_template('forms/update_incident.html', statuses = statuses, currentState = currentState, incident = incident)
