import os
from flask_sqlalchemy import SQLAlchemy
from model import User, db, connect_db
import requests
import json
from urllib.request import urlopen
from google.cloud import api_keys_v2
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, session, g, url_for, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import SearchBookForm, LoginForm, EditForm, RegistrationForm

app = Flask(__name__, '/static')

CURR_USER_KEY = "curr_user"

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://book.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_RECORD_QUERIES"] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "API_KEY"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    flash('Please login first.', 'danger')
    return redirect(url_for('login'))


API_KEY = 'AIzaSyCUg3r9gfvDYIa_y33XCA5wobD3S4do8g8'


@app.route('/')
def homepage():
    print(User)
    if CURR_USER_KEY in session:
        # User is logged in, perform actions
        return render_template('homepage.html')

    return redirect("/login")

    #######################################################
    # Login / register / logout
    #######################################################


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        # user = User.query.filter_by(
        # form.username.data, form.password.data).first()
        if user:
            do_login(user)
            flash('Welcome back {user.username}!', 'info')
            # Store user session data
            return redirect("/")
        flash("Invalid credentials.", 'danger')
    return render_template('users/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Handle logout of user."""
    # IMPLEMENT THIS
    logout_user()

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    flash("You have been logged out!")
    return redirect("/login")


@app.route('/register', methods=["GET", "POST"])
def register():
    # Register user: produce form and handle form submission
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User.register(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data
        )

        login_user(user)

        flash('Successfully created your account!', 'success')

        # Check if username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists. Please choose another."
        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template("users/login.html", form=form)

#######################################################
    # Book Interactions
#######################################################


@app.route('/bklist', methods=["GET", "POST"])
@login_required
def list_of_books():
    """Show all books that user liked"""
    print(g.user)
    booklist = []
    books = book.query.filter_by(user_id=current_user.id).all()
    # Now 'book' is properly assigned before usage in the template
    return render_template('bklist.html', bklist=booklist, books=books)


@app.route('/book', methods=["GET", "POST"])
def search_results():
    # Get the search query from the form on the homepage
    search_results = []
    book = None  # Initialize book as None to avoid UnboundLocalError
    form = SearchBookForm(request.form)

    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            # Make a request to the Google Books API
            base_url = 'https://www.googleapis.com/books/v1/volumes'
            API_KEY = os.getenv("API_KEY")
            params = {'q': query, 'key': API_KEY, 'maxResults': 5}
            response = requests.get(base_url, params=params)
            load_dotenv()

            if response.status_code == 200:
                data = response.json()
                search_results = data.get('items', [])

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract and pass the data to the template for rendering
        book = data.get("items", [])
        # Check if categories, description, or images exist in volumeInfo
        for book in book:
            if "description" not in book.get("volumeInfo", {}):
                book["volumeInfo"]["description"] = "Description not available"
            if "categories" not in book.get("volumeInfo", {}):
                book["volumeInfo"]["categories"] = ["N/A"]
            if "imageLinks" not in book.get("volumeInfo", {}):
                # If no thumbnail present, use a default image
                book["volumeInfo"]["imageLinks"] = {
                    "thumbnail": "https://cdn3.iconfinder.com/data/icons/minecraft-icons/512/Book.png"}

        return render_template('book.html', book=book, book_id=book_id, form=form, search_results=search_results, error_message=error_message)

    #######################################################
    # User Information and profile
    #######################################################


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    user = User.query.get_or_404(user_id)
    fav_book = []
    favorites = user.favorites
    for fv in favorites:
        if fv.user_id == user_id:
            book = request.get_book(fv.book_id)
            fav_book.append(book)

    return render_template('users/detail.html', user=user, fav_book=fav_book)


@app.route('/users/profile', methods=["GET", "POST"])
@login_required
def edit(user_id):
    """Update profile for current user."""
    user = User.query.get_or_404(user_id)
    form = EditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.password = form.password.data
            user.email = form.email.data
        db.session.commit()
        return redirect("/users/{user.id}")
    return render_template('users/edit.html', form=form, user_id=user_id)


@app.route('/users/delete', methods=["POST"])
@login_required
def delete_user():
    """Delete user."""
    user = User.query.get_or_404(current_user.id)
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")

    logout_user()

    db.session.delete(g.user)
    db.session.commit()
    flash('account removed.', 'info')
    return redirect("/register")

#######################################################
# error handling
#######################################################


@app.errorhandler(500)
def page_not_found(e):
    """when the search fails it returns 500, so redirect for that"""

    return render_template('badsearch.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
