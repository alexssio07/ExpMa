from flask import (
    Blueprint,
    make_response,
    render_template,
    redirect,
    session,
    url_for,
    request,
    flash,
)
from flask_login import login_user, logout_user, login_required
from app.database import db
from app.models import models
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint(
    "auth", __name__
)  # Registro il blueprint per le rotte API per l'autenticazione per poterlo importare in app/__init__.py


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = models.User.query.filter_by(username=username, password=password).first()
        if user and models.User.check_password(user, password):
            if login_user(user):
                session["username"] = user.username
                print("Login successful")
                flash("Login successful", "message")
                return redirect(url_for("main.home"))
            else:
                print("Login failed")
                flash("Login failed", "error")
                return render_template("login.html")
        else:
            print("Invalid username or password")
            flash("Invalid username or password", "error")
            return render_template("login.html")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash("Please enter a username and password", "error")
            return redirect(url_for("auth.register"))
        hashed_password = generate_password_hash(password, method="pbkdf2")
        new_user = models.User(username=username, password=password)
        new_user.set_hash_password(hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session["username"] = new_user.username
        print("Registration successful")
        flash("Registration successful", "message")
        return redirect(url_for("main.home"))

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    logout_user()
    resp = make_response(redirect(url_for("main.home")))
    resp.delete_cookie("session")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp
