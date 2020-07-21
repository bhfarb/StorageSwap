import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd, find_distance, check_dates, format_date

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filters
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["format_date"] = format_date

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///storageswap.db")


@app.route("/")
@login_required
def home():
    return render_template("search.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # Get username
    username = request.args.get("username").lower()

    # Get users with same username (if any)
    taken = db.execute("SELECT * FROM users WHERE username = :u", u=username)

    # Return true if no users with the same username and length of username > 0
    if (not taken and len(username) > 0):
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/buy", methods=["GET", "POST"])
def buy():
    """Register new buyer"""
    # Render template
    if (request.method == "GET"):
        return render_template("buy.html")

    if (request.method == "POST"):
        # Get inputs
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("confirmation")
        intro = request.form.get("intro")
        email = request.form.get("email")
        phone = request.form.get("phone")
        role = "buyer"

        # Return apology if missing entries
        if not username:
            return apology("You must enter a username.")
        if not intro:
            return apology("You must enter information about yourself.")
        if not password or not password2:
            return apology("You must enter a password and confirmation.")
        if not email:
            return apology("You must enter your email address.")
        if not phone:
            return apology("You must enter your phone number.")

        # Return apology if username taken
        taken = db.execute("SELECT * FROM users WHERE username = :u", u=username.lower())
        if (taken):
            return apology("Username is taken.")

        # Return apology if passwords don't match
        if (password != password2):
            return apology("Passwords must match.")

        # Hash password
        hash = generate_password_hash(password)

        # Add user to database
        db.execute("INSERT INTO users (username, hash, name, intro, email, phone, role) VALUES(:username, :hash, :name, :intro,:email, :phone, :role)",
                   username=username, hash=hash, name=name, intro=intro, email=email, phone=phone, role=role)

        # Redirect user to login form
        return redirect("/login")


@app.route("/sell", methods=["GET", "POST"])
def sell():
    """Register new sell user"""
    # Render template
    if (request.method == "GET"):
        return render_template("sell.html")

    if (request.method == "POST"):
        # Get inputs
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("confirmation")
        intro = request.form.get("intro")
        email = request.form.get("email")
        phone = request.form.get("phone")
        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")
        zip = request.form.get("zip")
        role = "seller"

        # Return apology if missing entries
        if not username:
            return apology("You must enter a username.")
        if not intro:
            return apology("You must enter information about yourself.")
        if not password or not password2:
            return apology("You must enter a password and confirmation.")
        if not email:
            return apology("You must enter your email address.")
        if not phone:
            return apology("You must enter your phone number.")
        if not street:
            return apology("You must enter your street address.")
        if not city:
            return apology("You must enter your city.")
        if not state:
            return apology("You must enter your state.")
        if not zip:
            return apology("You must enter your zip code.")

        # Return apology if username taken
        taken = db.execute("SELECT * FROM users WHERE username = :u", u=username.lower())
        if (taken):
            return apology("Username is taken.")

        # Return apology if passwords don't match
        if (password != password2):
            return apology("Passwords must match.")

        # Hash password
        hash = generate_password_hash(password)

        # Add user to database
        db.execute("INSERT INTO users (username, hash, name, street, city, state, zip, intro, email, phone, role) VALUES(:username, :hash, :name, :street, :city, :state, :zip, :intro, :email, :phone, :role)",
                   username=username, hash=hash, name=name, street=street, city=city, state=state, zip=zip, intro=intro, email=email, phone=phone, role=role)

        # Redirect user to login
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in, what their username is, and what their role is
        session["user_id"] = rows[0]["user_id"]
        session["username"] = rows[0]["username"]
        session["role"] = rows[0]["role"]

        # Check if user is buyer or seller
        role = db.execute("SELECT role FROM users WHERE user_id = :user_id", user_id=session["user_id"])

        # Redirect user to buyer or seller home page
        if role[0]["role"] == "buyer":
            return redirect("/search")
        if role[0]["role"] == "seller":
            return redirect("/make")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/make", methods=["GET", "POST"])
def make():
    """Make a listing"""
    # Render template
    if (request.method == "GET"):
        return render_template("make_listing.html")

    if (request.method == "POST"):
        # Get inputs
        space = int(request.form.get("space"))
        price = float(request.form.get("price"))
        start = str(request.form.get("start"))
        print(start)
        end = str(request.form.get("end"))
        print(end)
        setting = request.form.get("setting")
        user_info = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=session["user_id"])
        street = user_info[0]["street"]
        city = user_info[0]["city"]
        state = user_info[0]["state"]
        zip = user_info[0]["zip"]

        # Return apology if missing entries
        if not space:
            return apology("You must enter your available space.")
        if not price:
            return apology("You must enter your price.")
        if not start or not end:
            return apology("You must enter start and end dates.")
        if not setting:
            return apology("You must enter your setting.")

        # Add listing to database
        db.execute("INSERT INTO listings (user_id, street, city, state, zip, setting, space, price, start, end) VALUES(:user_id, :street, :city, :state, :zip, :setting, :space, :price, :start, :end)",
                   user_id=session["user_id"], street=street, city=city, state=state, zip=zip, setting=setting, space=space, price=price, start=start, end=end)

        # Redirect user to profile form
        return redirect("/profile/" + user_info[0]["username"])


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Buyer can search parameters for storage"""

    # Render template
    if (request.method == "GET"):
        return render_template("search.html")

    if (request.method == "POST"):

        # Get inputs
        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")
        zip = request.form.get("zip")
        miles = request.form.get("miles")
        space = request.form.get("space")
        start = request.form.get("start")
        end = request.form.get("end")

        # Return apology if missing entries
        if not city:
            return apology("You must enter your city.")
        if not state:
            return apology("You must enter your state.")
        if not zip:
            return apology("You must enter your zip code.")
        if not miles:
            return apology("You must enter the range.")
        if not space:
            return apology("You must enter the number of boxes.")
        if not start:
            return apology("You must enter the start date.")
        if not end:
            return apology("You must enter the end date.")

        # format the user's location
        loc_1 = street + ', ' + city + ', ' + state + ', ' + zip

        # find their prefered range in meters (1609.34 is the conversion rate)
        meters = 1609.34 * float(miles)

        # make a list of the of all listings
        listings = db.execute('SELECT * FROM listings')

        # make a list of of viable listings
        viable_listings = []

        # find which listings are within physical range
        for listing in listings:
            # format the location
            loc_2 = listing['street'] + ', ' + listing['city']+', ' + listing['state']+', ' + listing['zip']

            # find the distances
            distance_dict = find_distance(loc_1, loc_2)
            distance_text = distance_dict['text']  # str in metric units
            distance_value = distance_dict['value']  # int in meters

            # check if the listing is viable, if so add it to list
            if (distance_value <= meters) and (int(space) <= int(listing['space'])) and (check_dates(start, end, listing['start'], listing['end'])):

                # add distance to the listing
                listing['distance'] = distance_text

                # add listing to list of viable listings
                viable_listings.append(listing)

        # order the list of viable listings by price
        final_listings = sorted(viable_listings, key=lambda k: k['price'])

        # add names to the list final listings
        for listing in final_listings:
            listing['username'] = db.execute('SELECT username FROM users WHERE user_id=:user_id',
                                             user_id=listing['user_id'])[0]['username']

        # redirect to search results
        return render_template("search_results.html", final_listings=final_listings, loc_1=loc_1)


@app.route("/profile/<username>", methods=["GET"])
@login_required
def profile(username):
    if (request.method == "GET"):
        # Get info for current user
        user_info = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=session["user_id"])[0]

        # Get info for requested username url
        url_user_info = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        # Checks if it is profile of current user
        if username == user_info["username"]:
            if user_info["role"] == "buyer":
                return render_template("buyerprofile.html", user_info=user_info)

            if user_info["role"] == "seller":
                # find all listings for that user
                listings = db.execute("SELECT * from listings WHERE user_id = :user_id", user_id=session["user_id"])

                return render_template("sellerprofile.html", user_info=user_info, listings=listings)

            else:
                return apology("Your profile must be associated with buyer or seller.")

        # Makes sure queried for real username
        elif url_user_info:
            url_user_info = url_user_info[0]
            if url_user_info["role"] == "buyer":
                return render_template("buyerprofile.html", user_info=url_user_info)

            if url_user_info["role"] == "seller":
                # Find all listings for that user
                listings = db.execute("SELECT * from listings WHERE user_id = :user_id", user_id=url_user_info["user_id"])

            return render_template("sellerprofile.html", user_info=url_user_info, listings=listings)


@app.route("/listing/<listing_id>", methods=["GET"])
@login_required
def listing(listing_id):
    # Find the requested listing in database based on given id
    listing_info = db.execute("SELECT * from listings WHERE listing_id = :listing_id", listing_id=int(listing_id))[0]

    # Add username to listing info
    listing_info["username"] = db.execute("SELECT username from users WHERE user_id = :user_id",
                                          user_id=listing_info["user_id"])[0]["username"]

    # Render template based on whether current user is buyer or seller
    if session["role"] == "buyer":
        return render_template("listing_buyer.html", listing_info=listing_info)

    else:
        return render_template("listing_seller.html", listing_info=listing_info)


@app.route("/new_message/<username>", methods=["GET", "POST"])
@login_required
def new_message(username):
    """Send a message"""
    # Render template
    if (request.method == "GET"):
        return render_template("new_message.html", username=username)

    if (request.method == "POST"):
        # Get inputs
        message = request.form.get("message")

        # Add message to database
        db.execute("INSERT INTO messages (sender, receiver, message, time) VALUES (:sender, :receiver, :message, CURRENT_TIMESTAMP)",
                   sender=session["username"], receiver=username, message=message)

        return redirect("/messages")


@app.route("/messages", methods=["GET"])
@login_required
def messages():
    """Display messages sent and received"""
    # Get messages received and sent for user logged in
    received = db.execute("SELECT * FROM messages WHERE receiver = :receiver", receiver=session["username"])
    sent = db.execute("SELECT * FROM messages WHERE sender = :sender", sender=session["username"])
    # Render template
    return render_template("messages.html", received=received, sent=sent)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)