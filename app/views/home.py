from flask import Blueprint, render_template, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from app.models import Incident, User, Incident_History
from app.views.forms import tagNames
# import db here once it is made

# creating blueprint
blueprint = Blueprint("home", __name__)

class SearchIncident(FlaskForm):
    tagSearch = SelectField('Search for tags:', choices = [])
    pocSearch = SelectField('Search for point of contact:', choices = [])
    search = SubmitField('Search')

# dashboard route
@blueprint.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
    #queries db for all incidents and filters by incidentID
    Incidents = Incident.query.order_by(Incident.state.desc(), Incident.incidentID).all()
    contactNames = []

    for incident in Incidents:
        poc = incident.point_of_contact
        user = User.query.get(poc)
        point_of_contact = user.fname + " " + user.lname
        contactNames.append(point_of_contact)

    incidentZip = zip(Incidents, contactNames)

    form = SearchIncident()
    form.tagSearch.choices = [(tag, tag) for tag in tagNames]
    form.pocSearch.choices = [(user.id, str(user.fname + " " + user.lname)) for user in User.query.all()]

    if request.method == "POST":
        return search_incident(form)

    return render_template('home/dashboard.html', incidents = incidentZip, form = form)

# individual ticket route
@login_required
@blueprint.route('/ticket/<int:ticketID>')
def ticket(ticketID):
    #queries database for all incident history based on ticketID
    incident_history = Incident_History.query.filter_by(incident_id = ticketID).all()
    incident = Incident.query.get(ticketID)
    poc = User.query.get(incident.point_of_contact)
    assignee = User.query.get(incident.assignee)

    return render_template('home/ticket.html', history = incident_history, incident = incident, poc = poc, assignee = assignee)

# search for tags or point of contact
@login_required
@blueprint.route('/dashboard/search-results')
def search_incident(form):

    searchForm = SearchIncident()
    searchForm.tagSearch.choices = [(tag, tag) for tag in tagNames]
    searchForm.pocSearch.choices = [(user.id, str(user.fname + " " + user.lname)) for user in User.query.all()]

    if form.tagSearch.data != '':
        incidents = Incident.query.filter(Incident.tag.contains(form.tagSearch.data)).all()
    elif form.pocSearch.data != '':
        incidents = Incident.query.filter(Incident.point_of_contact == form.pocSearch.data).all()

    contactNames = []
    for incident in incidents:
        poc = incident.point_of_contact
        user = User.query.get(poc)
        point_of_contact = user.fname + " " + user.lname
        contactNames.append(point_of_contact)

    incidentZip = zip(incidents, contactNames)
    return render_template('home/dashboard.html', incidents = incidentZip, form = searchForm)
