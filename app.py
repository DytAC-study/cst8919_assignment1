import json
import logging
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request
import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flask-app")

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/")
def home():
    return render_template("home.html", session=session.get('user'))

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=f"https://flask-web-yuntiandu-240702.azurewebsites.net/callback"
    )

@app.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token["userinfo"]
    user = session["user"]
    logger.info(f"[LOGIN] user_id={user['sub']} email={user['email']} timestamp={datetime.datetime.utcnow()}")
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://{env.get('AUTH0_DOMAIN')}/v2/logout?" +
        urlencode({"returnTo": url_for("home", _external=True), "client_id": env.get("AUTH0_CLIENT_ID")}, quote_via=quote_plus)
    )

@app.route("/protected")
def protected():
    if "user" not in session:
        logger.warning(f"[UNAUTHORIZED] Attempt to access /protected at {datetime.datetime.utcnow()}")
        return "Unauthorized", 401
    user = session["user"]
    logger.info(f"[ACCESS] user_id={user['sub']} accessed /protected timestamp={datetime.datetime.utcnow()}")
    return f"Welcome {user['email']} to the protected route!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)