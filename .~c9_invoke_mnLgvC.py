import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

from helpers import apology, login_required

# Configure application
app = Flask(__name__, static_url_path="/static")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///registrants.db")


# Index route
@app.route("/", methods=["GET", "POST"])
def index():
    if session:
        id = session["user_id"]
        username = db.execute("SELECT username FROM login WHERE id=:id", id=id)[0]["username"]
        return render_template("index.html", username=username)
    else:
        return render_template("index.html")


# find place request returning json value of search results
# https://maps.googleapis.com/maps/api/place/findplacefromtext/output?parameters
# example find place request for "mongolian grill"
# https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=mongolian%20grill&inputtype=textquery&fields=photos,formatted_address,name,opening_hours,rating&locationbias=circle:2000@47.6918452,-122.2226413&key=YOUR_API_KEY

# test page
@app.route("/test")
def test():
    return render_template("test.html")

# submitted location in search bar
@app.route("/restaurants", methods=["GET", "POST"])
def restaurants():
    username = []
    # if submitted location in search bar
    if session:
        id = session["user_id"]
        username = db.execute("SELECT username FROM login WHERE id=:id", id=id)[0]["username"]
    if request.method == "POST":
        # check for proper submission
        address = request.form.get("address")
        if not address:
            return apology("Enter a location!")
        else:
            if username:
                return render_template("restaurants.html", username=username, address=address)
            else:
                return render_template("restaurants.html", address=address)
    # if they just got to restaurants.html by accident
    else:
        if username:
            return render_template("restaurants.html", username=username)
        else:
            return render_template("restaurants.html")


# if registered, go to index.html with welcome message
# if not, go to register.html to sign up
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Query database for username
    rows = db.execute("SELECT * FROM login")
    # If form was posted
    if request.method == "POST":
        # if username is blank, return apology
        if not request.form.get("username"):
            return apology("Missing username!")
        # if password is blank, return apology
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Missing password!")
        # if passwords do not match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match!")
        # if username already exists in db, return apology
        elif db.execute("SELECT * FROM login WHERE username=:username",
                        username=request.form.get("username")):
            return apology("Username taken.")
        # register the new user
        else:
            # hash password before storing using pwd_context.encrypt
            hash = generate_password_hash(request.form.get("password"))
            # add user to database
            result = db.execute("INSERT INTO login (username, hash) VALUES(:username, :hash)",
                                username=request.form.get("username"), hash=hash)
            # this error should not happen because we already checked to make sure
            # it is a unique username, but if it does, return a database error.
            if not result:
                return apology("Database error.")
            # login user automatically after registering
            rows = db.execute("SELECT * FROM login WHERE username=:username",
                              username=request.form.get("username"))
            session["user_id"] = rows[0]["id"]

            # pop-up message of registration
            flash("Registered!")

            return redirect("/")
    # if going to register page without posting form
    else:
        return render_template("register.html")

# if they logged in successfully, go to restaurants.html where they can search for an address and see a couple recommended restaurants
# if they just clicked log in, go to login.html
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        """Log User in"""
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide a valid password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM login WHERE username = :username", username = request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")