"""Models for Notes app."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database to provided Flask app"""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User."""

    __tablename__ = "users"

    username = db.Column(db.String(20),
                   primary_key=True)
    password = db.Column(db.Text,
                       nullable=False)
    email = db.Column(db.String(50),
                       nullable=False,
                       unique=True)
    first_name = db.Column(db.String(30),
                       nullable=False)
    last_name = db.Column(db.String(30),
                       nullable=False)


    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd).decode('utf8')

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed, email=email, 
        first_name=first_name, last_name=last_name)


    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = cls.query.filter_by(username=username).one_or_none()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False