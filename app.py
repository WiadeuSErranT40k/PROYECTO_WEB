from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "clave_secreta"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('antonito.db')
    conn.row_factory = sqlite3.Row
    return conn

# Página principal
@app.route("/")
def index():
    conn = get_db_connection()
    productos = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("Inicio.html", productos=productos)

# Subida de producto
@app.route("/add_product", methods=["POST"])
def add_product():
    if 'username' not in session:
        return redirect(url_for("index"))

    name = request.form["name"]
    category = request.form["category"]
    features = request.form["features"]
    price = request.form["price"]
    image = request.files["image"]

    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        return "No se subió imagen", 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO products (name, category, features, price, image_filename) VALUES (?, ?, ?, ?, ?)",
        (name, category, features, price, filename)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# Login
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    conn.close()

    if user:
        session["username"] = username
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# Registro (opcional, si decides permitir registros nuevos)
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return "Usuario ya existe", 409
    finally:
        conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
#==================================================================================================================
# Crear la estructura de base de datos en SQLite para el sistema solicitado.
"""import sqlite3

# Crear la base de datos y la conexión
conn = sqlite3.connect("antonito.db")
c = conn.cursor()

# Crear tabla de usuarios
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Crear tabla de productos
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    features TEXT NOT NULL,
    price REAL NOT NULL,
    image_filename TEXT NOT NULL
)
''')

conn.commit()
conn.close()
"""
#==================================================================================================================