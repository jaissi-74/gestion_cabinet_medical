from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
from pathlib import Path
import csv
from flask import Response

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB_PATH = Path(__file__).resolve().parent / "contacts.db"


def connect():
    return sqlite3.connect(DB_PATH)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS contacts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        category TEXT,
        adress TEXT,
        company TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rdv(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER NOT NULL,
        date_rdv TEXT NOT NULL,
        heure_rdv TEXT NOT NULL,
        motif TEXT,
        FOREIGN KEY(contact_id) REFERENCES contacts(id)
    )
    """)
    try:
        cur.execute("INSERT INTO admins(username, password_hash) VALUES (?, ?)", ("admin", hash_password("admin123")))
    except Exception:
        pass
    conn.commit()
    conn.close()


def require_login():
    return session.get("admin") is True


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT id FROM admins WHERE username=? AND password_hash=?", (username, password))
        admin = cur.fetchone()
        conn.close()
        if admin:
            session["admin"] = True
            return redirect(url_for("contacts"))
        flash("Identifiants incorrects", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/contacts")
def contacts():
    if not require_login():
        return redirect(url_for("login"))
    q = request.args.get("q", "")
    conn = connect()
    cur = conn.cursor()
    if q:
        like = f"%{q}%"
        cur.execute("""
            SELECT * FROM contacts
            WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR category LIKE ?
            ORDER BY name
        """, (like, like, like, like))
    else:
        cur.execute("SELECT * FROM contacts ORDER BY name")
    data = cur.fetchall()
    conn.close()
    return render_template("contacts.html", contacts=data, q=q)


@app.route("/add", methods=["GET", "POST"])
def add_contact():
    if not require_login():
        return redirect(url_for("login"))
    if request.method == "POST":
        data = (
            request.form["name"], request.form["email"], request.form["phone"],
            request.form.get("category", ""), request.form.get("adress", ""), request.form.get("company", "")
        )
        conn = connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO contacts(name,email,phone,category,adress,company)
                VALUES(?,?,?,?,?,?)
            """, data)
            conn.commit()
            flash("Contact ajouté", "success")
            return redirect(url_for("contacts"))
        except Exception:
            flash("Email déjà utilisé ou données incorrectes", "danger")
        finally:
            conn.close()
    return render_template("form.html", contact=None)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_contact(id):
    if not require_login():
        return redirect(url_for("login"))
    conn = connect()
    cur = conn.cursor()
    if request.method == "POST":
        data = (
            request.form["name"], request.form["email"], request.form["phone"],
            request.form.get("category", ""), request.form.get("adress", ""), request.form.get("company", ""), id
        )
        cur.execute("""
            UPDATE contacts SET name=?, email=?, phone=?, category=?, adress=?, company=?
            WHERE id=?
        """, data)
        conn.commit()
        conn.close()
        flash("Contact modifié", "success")
        return redirect(url_for("contacts"))
    cur.execute("SELECT * FROM contacts WHERE id=?", (id,))
    contact = cur.fetchone()
    conn.close()
    return render_template("form.html", contact=contact)


@app.route("/delete/<int:id>")
def delete_contact(id):
    if not require_login():
        return redirect(url_for("login"))
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Contact supprimé", "success")
    return redirect(url_for("contacts"))


@app.route("/rdv", methods=["GET", "POST"])
def rdv():
    if not require_login():
        return redirect(url_for("login"))
    conn = connect()
    cur = conn.cursor()
    if request.method == "POST":
        cur.execute(
            "INSERT INTO rdv(contact_id,date_rdv,heure_rdv,motif) VALUES(?,?,?,?)",
            (request.form["contact_id"], request.form["date_rdv"], request.form["heure_rdv"], request.form["motif"])
        )
        conn.commit()
        flash("RDV ajouté", "success")
    cur.execute("SELECT id, name FROM contacts ORDER BY name")
    contacts_data = cur.fetchall()
    cur.execute("""
        SELECT rdv.id, contacts.name, rdv.date_rdv, rdv.heure_rdv, rdv.motif
        FROM rdv JOIN contacts ON contacts.id=rdv.contact_id
        ORDER BY rdv.date_rdv, rdv.heure_rdv
    """)
    rdvs = cur.fetchall()
    conn.close()
    return render_template("rdv.html", contacts=contacts_data, rdvs=rdvs)


@app.route("/rdv/delete/<int:id>")
def delete_rdv(id):
    if not require_login():
        return redirect(url_for("login"))
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM rdv WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("RDV supprimé", "success")
    return redirect(url_for("rdv"))

@app.route("/export_csv")
def export_csv():

    if not require_login():
        return redirect(url_for("login"))

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT name,email,phone,category,address,company
        FROM contacts
        ORDER BY name
    """)

    contacts = cur.fetchall()
    conn.close()

    output = []

    output.append(
        "Nom,Email,Téléphone,Catégorie,Adresse,Entreprise\n"
    )

    for c in contacts:
        output.append(
            f"{c[0]},{c[1]},{c[2]},{c[3]},{c[4]},{c[5]}\n"
        )

    return Response(
        "".join(output),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=contacts.csv"
        }
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
