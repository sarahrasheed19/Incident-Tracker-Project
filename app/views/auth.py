from flask import Blueprint, render_template, redirect, url_for, flash
from app import app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db

# creating blueprint
blueprint = Blueprint("auth", __name__)

#form for logging in
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(max=30)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

#form for registering for an account
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=40)])
    username = StringField('Username', validators=[InputRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(max=30)])
    fname = StringField('First Name', validators=[InputRequired(), Length(max=20)])
    lname = StringField('Last Name', validators=[InputRequired(), Length(max=25)])
    submit = SubmitField('Register')

#form for resetting password
class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    old_password = PasswordField('Old Password', validators=[InputRequired()])
    new_password = PasswordField('New Password', validators=[InputRequired()])
    submit = SubmitField('Reset')

# @login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#login route
@blueprint.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home.dashboard'))


    return render_template('auth/login.html', form = form)

#Register route
@blueprint.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username = form.username.data, email = form.email.data, password = hashed_password, fname = form.fname.data, lname = form.lname.data, userType="User", incident_created=None, incident_assigned=None)

        db.session.add(new_user)
        db.session.commit()

    return render_template('auth/register.html', form=form)

#Password reset route
@blueprint.route('/reset-password', methods = ['GET', 'POST'])
def reset_password():
    form = PasswordResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            if check_password_hash(user.password, form.old_password.data):
                new_pass_hashed = generate_password_hash(form.new_password.data, method='sha256')
                user.password = new_pass_hashed
                db.session.commit()

                flash('Password sucessfully reset.')
                return redirect(url_for('login'))

    return render_template('auth/reset_password.html', form=form)

#logout route
@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
