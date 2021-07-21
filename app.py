"""Flask app for Cupcakes"""

from flask import Flask, render_template, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Note
from forms import CreateUserForm, LoginUserForm, AddNoteForm, EditNoteForm

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

        return redirect("/login")

    return render_template("create_user_form.html", form=form)


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
            session["username"] = user.username  # keep logged in
            return redirect(f"/users/{name}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login_user_form.html", form=form)


@app.route("/logout", methods=["POST"])
def logout():
    """Logs user out and redirects to login page."""

    # Remove "username" if present, but no errors if it wasn't
    session.pop("username", None)

    return redirect("/login")


@app.route("/users/<username>")
def load_user_profile(username):
    """Handles user profile page for logged-in users only"""

    if "username" not in session or username != session["username"]:
        flash("You must be logged in to view!")
        return redirect("/login")

    user = User.query.get_or_404(username)
    notes = Note.query.filter(Note.owner ==username).all()
    # TODO: this is where the relationship would come into play! would just 
    #need to use user.notes for notes

    return render_template("user_profile.html",
                            user=user,
                            notes=notes)


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user_profile(username):
    """Removes user from the database and removes their notes
     from database. Redirects to "/" """

    if "username" not in session or username != session["username"]:
        flash("You must be logged in to view!")
        return redirect("/login")

    user = User.query.get_or_404(username)
    user_notes = Note.query.filter(Note.owner == username).all()
    #TODO: same as previous route
    
    for note in user_notes:
        db.session.delete(note)
    db.session.delete(user)

    db.session.commit()

    return redirect("/")


@app.route("/users/<username>/notes/add", methods=["GET", "POST"])
def add_note(username):
    """Handles add note form:
    if GET: loads form
    if POST: handles form to add note"""

    if "username" not in session or username != session["username"]:
        flash("You must be logged in to view!")
        return redirect("/login")

    form = AddNoteForm()
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_note = Note(title = title,
                         content = content,
                         owner = username)

        db.session.add(new_note)
        db.session.commit()

        return redirect(f"/users/{username}")

    return render_template("add_note_form.html", form=form)


@app.route("/notes/<note_id>/update", methods=["GET", "POST"])
def edit_note(note_id):
    """Handles edit note form:
    if GET: loads form
    if POST: handles form to edit note"""

    note = Note.query.get_or_404(note_id)

    if "username" not in session or note.owner != session["username"]:
        flash("You must be logged in to view!")
        return redirect("/login")

    form = EditNoteForm()
    username = session["username"]
    
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{username}")

    return render_template("edit_note_form.html", form=form)


@app.route("/notes/<note_id>/delete", methods=["POST"])
def delete_note(note_id):
    """Removes note from the database and redirects to 
    /users/<username>"""
    
    note = Note.query.get_or_404(note_id)

    if "username" not in session or note.owner != session["username"]:
        flash("You must be logged in to view!")
        return redirect("/login")

    username = session["username"]
    
    db.session.delete(note)
    db.session.commit()

    return redirect(f"/users/{username}")

