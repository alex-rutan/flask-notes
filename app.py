"""Flask app for Cupcakes"""

from flask import Flask, render_template, redirect, jsonify, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import CreateUserForm, LoginUserForm

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret"

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///notes"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route("/")
def redirect_to_register():
    """Redirects to "/register" """

    return redirect("/register")


@app.route("/register", methods=["GET", "POST"]) 
def create_user():
    """Handles create user form:
    if GET: loads form
    if POST: handles form to create user instance"""

    form = CreateUserForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email,
        first_name, last_name)

        db.session.add(new_user)
        db.session.commit()

        return redirect('/secret')

    else:
        return render_template('create_user_form.html', form=form)


@app.route("/login", methods=["GET", "POST"]) 
def login_user():
    """Handles login user form:
    if GET: loads form
    if POST: handles form to login user"""

    form = LoginUserForm()
    
    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(name, pwd)

        if user:
            session["user_username"] = user.username  # keep logged in
            return redirect("/secret")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template('login_user_form.html', form=form)


@app.route("/secret")
def secret():
    """Handles secret page for logged-in users only"""

    return "You made it!"
