from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy import ForeignKey

# Create the SQLAlchemy instance
db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)  # Initialize the app with the database configuration
    return db

# Define a function to connect to the database


@classmethod
class Book(db.Model, UserMixin):
    __tablename__ = "book"  # Defines the table name
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    subjects = db.Column(db.String(255))
    thumbnail_url = db.Column(db.String(255))
    user_id = db.Column(db.Integer, ForeignKey('users.id', ondelete='cascade'))
    user = db.relationship('User', backref="mylibrary")

    @classmethod
# retrieve a users favorite book list "mylibrary"
    class List(db.Model):
        __tablename__ = 'mylibrary'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        book_id = db.Column(db.Text, nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @classmethod
    def addfavlist(user_id, book_id, mylibrary):
        """adds a favorite to the database tied to a user id"""

        fav_book = mylibrary(
            user_id=user_id,
            book_id=book_id
        )
        db.session.add(fav_book)
        return fav_book


@classmethod
class User(db.Model):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False,  unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    favorites = db.relationship('fav_book')

   # def __repr__(self):
    #  return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def register(cls, form):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(
            form['password']).decode('UTF-8')

        user = User(
            username=form['username'],
            password=hashed_pwd,
            email=form['email'],
        )

        db.session.add(user)
        db.session.commit()

        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
