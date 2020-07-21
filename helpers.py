import requests
import urllib.parse
import sys
import json

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import datetime as dt


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def format_date(value):
    """Format date as mm/dd/yy"""
    return dt.strptime(value, "%Y-%m-%d").strftime("%m/%d/%y")


def find_distance(loc_1, loc_2):
    """Find driving distance"""

    # define API key made using free trial
    my_key = 'AIzaSyCe7MqVNOtQ-3dhBxZqNXX-gq0WCInJBq4'

    # url variable store url
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

    # contact API
    try:
        # Get method of requests module
        # return response object
        r = requests.get(url + 'units=imperial'+'&origins=' + loc_1 +
                         '&destinations=' + loc_2 +
                         '&key=' + my_key)
    except requests.RequestException:
        return None

    # parse response
    try:
        # convert to json
        output = r.json()
        # find distance in miles and meters
        my_dist = output['rows'][0]['elements'][0]['distance']
        return my_dist
    except (KeyError, TypeError, ValueError):
        return None


def check_dates(range1_start, range1_end, range2_start, range2_end):
    """Checks if one date range falls within another"""
    # checks if range1 is in range2

    # assumes format is yyyy/mm/dd
    range1_start = dt.strptime(range1_start, "%Y-%m-%d")
    range1_end = dt.strptime(range1_end, "%Y-%m-%d")
    range2_start = dt.strptime(range2_start, "%Y-%m-%d")
    range2_end = dt.strptime(range2_end, "%Y-%m-%d")

    return (range1_start >= range2_start) and (range1_end <= range2_end)

