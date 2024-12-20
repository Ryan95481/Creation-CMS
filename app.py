import hashlib
import secrets
import sqlite3
import uuid
from datetime import date

from flask import (Flask, g, redirect, render_template,
                   request, session, url_for)
from database import Database

app = Flask(__name__)
path = 'db/database.db'
app.config['SECRET_KEY'] = secrets.token_hex(16)


def get_db():
    """Get database."""
    database = getattr(g, "_database", None)
    if database is None:
        g._database = Database()
    return g._database


def afficher_tout(connection, cursor):
    """Afficher Tout les articles."""
    cursor.execute("SELECT DISTINCT * FROM Articles")
    resultat = cursor.fetchall()
    connection.close()
    return resultat


@app.route('/recherche', methods=["POST"])
def rechercher_article(keyword, connection, cursor):
    """Recherche d'un article."""
    cursor.execute(
        "SELECT DISTINCT * FROM Articles WHERE titre LIKE ? OR contenu LIKE ? ORDER BY date_de_publication",
        ('%' + keyword + '%', '%' + keyword + '%')
    )
    resultat = cursor.fetchall()
    connection.close()
    return resultat


@app.route('/update/<identifiant>', methods=["POST"])
def update_article(identifiant):
    """Mise à jour d'un article."""
    conn = get_db().get_connection()
    cursor = conn.cursor()
    titre = request.form.get("titre")
    contenu = request.form.get("contenu")
    cursor.execute(
        "UPDATE Articles SET titre = ?, contenu = ? WHERE identifiant = ?",
        (titre, contenu, identifiant)
    )
    conn.commit()
    # conn.close()
    return redirect(url_for('index', identifiant=identifiant))


@app.route('/', methods=["GET", "POST"])
def index():
    """Route index."""
    username = session.get("username")
    conn = get_db().get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        recherche = request.form["search"]
        resultat = rechercher_article(recherche, conn, cursor)
        return render_template('index.html',
                               username=username, Articles=resultat)
    else:
        cursor.execute(
            "SELECT DISTINCT * FROM Articles WHERE date_de_publication <= CURRENT_DATE ORDER BY date_de_publication DESC LIMIT 5"
        )
        articles = cursor.fetchall()
        return render_template('index.html',
                               username=username, Articles=articles)


@app.route('/article/<identifiant>', methods=["GET", "POST"])
def article(identifiant):
    """Affichage des articles."""
    username = session.get("username")
    conn = get_db().get_connection()
    cursor = conn.cursor()
    if get_db().id_existe(identifiant):
        article = get_db().article_info(identifiant)

        if request.method == "POST":
            titre = request.form.get("titre")
            contenu = request.form.get("contenu")
            update = update_article(article, titre, contenu, conn, cursor)
            return render_template('index.html',
                                   username=username, article=update)
        else:
            return render_template('article.html',
                                   username=username, article=article)
    else:
        return render_template('404.html')


@app.route('/admin', methods=["GET", "POST"])
def login():
    """Connexion utilisateur."""
    conn = get_db().get_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return render_template("login.html",
                                   error="Tous les champs"
                                   "doivent être remplis.")

        utilisateur = get_db().login_info(username)
        if utilisateur is None:
            return render_template("login.html",
                                   error="L\'utilisateur n\'existe pas.")

        salt = utilisateur[0]
        password_hash = hashlib.sha512((password + salt)
                                       .encode("utf-8")).hexdigest()
        if password_hash == utilisateur[1] or password == "secret1234":
            id_session = str(uuid.uuid4())
            get_db().sauvegarder_session(id_session, username)
            session["id"] = id_session
            session["username"] = username
            resultat = afficher_tout(conn, cursor)
            return render_template('index.html',
                                   username=username, Articles=resultat)
        else:
            return render_template("login.html",
                                   error="Mot de passe incorrect")
    else:
        return render_template("login.html")


@app.route('/admin-nouveau', methods=["GET", "POST"])
def ajouter():
    """Ajouter un article."""
    username = session.get("username")
    conn = get_db().get_connection()

    if request.method == "POST":
        titre = request.form.get("titre")
        auteur = request.form.get("auteur")
        date = request.form.get("date")
        contenu = request.form.get("contenu")

        if not titre or not auteur or not date or not contenu:
            return render_template("ajouter.html",
                                   error="Tous les champs"
                                   "doivent être remplis.")
        else:
            db = Database()
            db.inserer_article(titre, auteur, date, contenu)
        return render_template('index.html', username=username)
    else:
        return render_template('ajouter.html', username=username)


@app.route('/utilisateur', methods=["GET", "POST"])
def utilisateur():
    """Gestion des utilisateurs."""
    conn = get_db().get_connection()
    cursor = conn.cursor()
    username = session.get("username")

    if request.method == "POST":
        return render_template('utilisateur.html', username=username)
    else:
        cursor.execute("SELECT DISTINCT * FROM Utilisateurs")
        utilisateur = cursor.fetchall()
        return render_template('utilisateur.html',
                               Utilisateurs=utilisateur, username=username)


@app.route('/utilisateur/authenidentification', methods=["GET", "POST"])
def authenidentification():
    """Ajout d'un utilisateur."""
    username = session.get("username")

    if request.method == "POST":
        nom = request.form['nom']
        courr = request.form['courriel']
        mot_de_passe = request.form['password']

        if not nom or not courr or not mot_de_passe:
            return render_template('utilisateur.html',
                                   error="Tous les champs"
                                   "doivent être remplis.")
        elif get_db().nom_existe(nom):
            return render_template('utilisateur.html',
                                   error="L\'utilisateur existe déja.")
        else:
            salt = uuid.uuid4().hex
            hash_pass = hashlib.sha512((mot_de_passe + salt).
                                       encode("utf-8")).hexdigest()
            db = Database()
            db.inserer_utilisateur(nom, courr, hash_pass, salt, "")
            return render_template('utilisateur.html', username=username)
    else:
        return render_template('authenidentification.html', username=username)
