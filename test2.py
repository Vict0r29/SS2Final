import datetime
from urllib.parse import unquote
from flask import Flask, jsonify
from google.auth import jwt

app = Flask(__name__)


@app.route('/')
def login():
    x = "ttps://lh3.googleusercontent.com/a/AGNmyxYEeWP_uvVsHZN6sMLMVPrPN-ePV--6Z4YQh3kT=s96-c"
    print(unquote(x))

login()
