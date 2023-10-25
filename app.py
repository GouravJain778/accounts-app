from flask import Flask, redirect, render_template, flash, url_for, session, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)
app.secret_key = "your_secret_key_here"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "profile"

mysql = MySQL(app)


# this function is for homw page rendring index.html
# TODO : update this function
@app.route("/index", methods=["GET", "POST"])
def index():
    if "login" in session:
        return render_template("index.html")
    return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    msg = ""
    if (
        request.method == "POST"
        and request.form["username"]
        and request.form["password"]
    ):
        username = request.form["username"]
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE username = username AND password = password"
        )
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]
            msg = "Logged in successfully !"

            return redirect("index")
        else:
            msg = "Incorrect username / password !"

    else:
        return render_template("login.html", msg=msg)


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/register", methods=["POST", "GET"])
def register():
    msg = ""
    if request.method == "POST" and (
        "username" in request.form
        and "password" in request.form
        and "email" in request.form
        and "organisation" in request.form
        and "country" in request.form
        and "postalcode" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        organisation = request.form["organisation"]
        state = request.form["state"]
        country = request.form["country"]
        postalcode = request.form["postalcode"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE username = username")
        account = cursor.fetchone()

        if account:
            meg = "Account already exists !"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address !"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "name must contain only characters and numbers !"
        else:
            cursor.execute(
                "INSERT INTO accounts (username, password, email, organisation, state, country, postalcode) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (username, password, email, organisation, state, country, postalcode),
            )

            mysql.connection.commit()
            msg = "You have successfully registered !"

    elif request.method == "POST":
        msg = "Please fill out the form !"
    return render_template("register.html", msg=msg)


@app.route("/update", methods=["POST", "GET"])
def update():
    msg = ""
    if session["login"]:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            email = request.form["email"]
            organisation = request.form["organisation"]
            state = request.form["state"]
            country = request.form["country"]
            postalcode = request.form["postalcode"]
            # Establish a database connection
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Fetch the user record by id
            cursor.execute(f'SELECT * FROM accounts WHERE id ={session["id"]}')
            account = cursor.fetchone()

            if account:
                # Update user information here
                cursor.execute(
                    "UPDATE accounts SET username=%s, password=%s, email=%s, organisation=%s, state=%s, country=%s, postalcode=%s WHERE id=%s",
                    (
                        username,
                        password,
                        email,
                        organisation,
                        state,
                        country,
                        postalcode,
                        session["id"],
                    ),
                )

                mysql.connection.commit()
                msg = "User information updated successfully"
            else:
                msg = "User not found"

            cursor.close()
            return redirect("display")

        else:
            return render_template("update.html")

        # Redirect or render template based on your application's logic
        # ...
    else:
        # Handle the case when the user is not logged in
        # ...
        return redirect("login")

    # Render a template or return a response based on your application's logic
    # ...


@app.route("/display")
def display():
    if session["loggedin"]:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM accounts WHERE id = {session["id"]}')
        account = cursor.fetchone()
        return render_template("display.html", account=account)
    return redirect(url_for("login"))


app.run(debug=True)
