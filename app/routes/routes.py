from cgitb import text
import os
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required

from app.models.models import Spesa

routes_bp = Blueprint("main", __name__)

css_classes = {
    "dark": [{"navbar": "navbar-dark"}, {"bg": "bg-dark"}, {"text-color": "text-white"}],
    "light": [{"navbar": "navbar-light"}, {"bg": "bg-light"}, {"text-color": "text-dark"}],
}


@routes_bp.route("/login")
def login():
    return render_template("login.html")


@routes_bp.route("/register")
def register():
    return render_template("register.html")


@routes_bp.route("/")
@routes_bp.route("/home")
@login_required
def home():
    theme_session = session.get("theme", "light")
    navbar_class = css_classes[theme_session][0].get("navbar")
    bg_class = css_classes[theme_session][1].get("bg")
    text_color = css_classes[theme_session][2].get("text-color")
    username = session.get("username")

    return render_template(
        "index.html",
        username=username,
        theme=theme_session,
        navbar_class=navbar_class,
        bg_class=bg_class,
        text_color=text_color
    )


@routes_bp.route("/dashboard")
@routes_bp.route("/dashboard/<int:page>")
@login_required
def dashboard(page=1):
    items_for_page = 10
    spese_complete = Spesa.query.all()
    pagination = Spesa.query.order_by(Spesa.id).paginate(page=page, per_page=items_for_page, error_out=False)
    # Get all expenses from database
    spese = pagination.items
    # Calculate totals
    total_income = 0
    total_expenses = 0
    for s in spese_complete:
        print(f"Spesa: {s.tipologia_pagamento} - Nome: {s.nome} - Descrizione: {s.descrizione} Importo: {s.importo}")
        if s.tipologia_pagamento == "Accredito":
            total_income += s.importo
        elif s.tipologia_pagamento == "Addebito":
            total_expenses -= s.importo

    # TO DO DA MIGLIORARE
    if session.get("theme") is not None:
        navbar_class = css_classes[session.get("theme")][0].get("navbar")
        bg_class = css_classes[session.get("theme")][1].get("bg")
        text_color = css_classes[session.get("theme")][2].get("text-color")
        return render_template(
            "dashboard.html",
            username=session.get("username"),
            theme=session.get("theme"),
            navbar_class=navbar_class,
            bg_class=bg_class,
            text_color=text_color,
            spese=spese,
            pagination=pagination,
            total_income=total_income,
            total_expenses=total_expenses
        )
    elif session.get("username") is not None:
        return render_template(
            "dashboard.html",
            username=session.get("username"),
            theme="light",
            navbar_class="navbar-light",
            bg_class="bg-light",
            text_color="text-dark",
            spese=spese,
            pagination=pagination,
            total_income=total_income,
            total_expenses=total_expenses
        )
    else:
        return render_template(
            "dashboard.html", 
            username=None, 
            theme="light", 
            navbar_class="navbar-light", 
            bg_class="bg-light",
            text_color="text-dark",
            spese=spese,
            pagination=pagination,
            total_income=total_income,
            total_expenses=total_expenses
        )
    



@routes_bp.route("/categories")
@login_required
def categories():
    if session.get("theme") != None:
        navbar_class = css_classes[session.get("theme")][0].get("navbar")
        bg_class = css_classes[session.get("theme")][1].get("bg")
        text_color = css_classes[session.get("theme")][2].get("text-color")
        if check_user_session() != None and navbar_class != None and bg_class != None:
            return render_template(
                "categories.html",
                username=session["username"],
                theme=session.get("theme"),
                navbar_class=navbar_class,
                bg_class=bg_class,
                text_color=text_color
            )
        else:
            return render_template("categories.html", username=None, theme="light", navbar_class="navbar-light", bg_class="bg-light")


@routes_bp.route("/settings")
@login_required
def settings():
    if session.get("theme") != None:
        navbar_class = css_classes[session.get("theme")][0].get("navbar")
        bg_class = css_classes[session.get("theme")][1].get("bg")
        text_color = css_classes[session.get("theme")][2].get("text-color")
        if check_user_session() != None and navbar_class != None and bg_class != None:
            return render_template(
                "settings.html",
                username=session["username"],
                theme=session.get("theme"),
                navbar_class=navbar_class,
                bg_class=bg_class,
                text_color=text_color
            )
        else:
            return render_template("settings.html", username=None, theme="light", navbar_class="navbar-light", bg_class="bg-light", text_color="text-dark")


@routes_bp.route("/toggle_theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"
    print(f"Current theme: {current_theme}")
    return redirect(url_for("main.home"))


def check_user_session():
    if session.get("username") != None and session.get("username") != "":
        return session["username"]
    return None


@routes_bp.route("/spese", methods=["GET"])
def get_spese():
    all_spese = Spesa.query.all()
    result = [
        {
            "id": spesa.id,
            "descrizione": spesa.descrizione,
            "data_operazione": spesa.data_operazione,
            "importo": spesa.importo,
            "categoria_id": spesa.categoria_id,
        }
        for spesa in all_spese
    ]
    return jsonify(result)
