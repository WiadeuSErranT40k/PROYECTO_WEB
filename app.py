#==================================================================================================================
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from markupsafe import Markup
import sqlite3
import os
import threading
import time
from datetime import datetime
from werkzeug.utils import secure_filename

# Configuración inicial
app = Flask(__name__)
app.secret_key = "clave_secreta"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Manejador de errores global
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"❌ Error no manejado: {str(e)}")
    return f"Error del servidor: {str(e)}", 500

@app.errorhandler(404)
def not_found_error(error):
    return "Página no encontrada", 404

@app.errorhandler(500)
def internal_error(error):
    return "Error interno del servidor", 500

# Función para conectarse a la base de datos
def get_db_connection():
    conn = sqlite3.connect('antonito.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear tabla de visitas si no existe
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            user_agent TEXT,
            timestamp TEXT
        );
    """)
    conn.commit()
    conn.close()

# Función para verificar si el usuario es admin
def is_admin():
    return session.get('username') == 'admin'

# Función para obtener el ID del usuario actual
def get_current_user_id():
    if 'username' not in session:
        return None
    
    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE username = ?", (session['username'],)).fetchone()
    conn.close()
    return user['id'] if user else None

# Función para encriptar datos de tarjeta (simplificado para demo)
def encrypt_card_data(card_number):
    # En producción, usar una librería de encriptación real
    return card_number[-4:] if len(card_number) >= 4 else card_number

# Ruta principal
@app.route("/")
def index():
    # Obtener IP real y User-Agent
    ip = request.headers.get("CF-Connecting-IP") or \
         request.headers.get("X-Forwarded-For") or \
         request.remote_addr
    user_agent = request.headers.get("User-Agent")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar visita en la base de datos
    conn = get_db_connection()
    conn.execute("INSERT INTO visits (ip, user_agent, timestamp) VALUES (?, ?, ?)", (ip, user_agent, timestamp))
    
    # Obtener productos con información de categoría y creador
    productos = conn.execute("""
        SELECT p.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
               u.username as created_by_username
        FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.created_by = u.id
        WHERE p.is_active = 1
        ORDER BY c.name, p.name
    """).fetchall()
    
    # Obtener categorías para el formulario
    categorias = conn.execute("SELECT * FROM categories WHERE is_active = 1 ORDER BY name").fetchall()
    
    # Debug simple
    print(f"🔍 DEBUG: {len(productos)} productos, {len(categorias)} categorías")
    for prod in productos:
        print(f"   📦 {prod['name']} -> {prod['category_name']}")
    
    conn.commit()
    conn.close()

    print(f"🛰️ Visita desde IP: {ip} - {user_agent}")
    return render_template("Inicio.html", productos=productos, categorias=categorias)

# Subida de producto
@app.route("/add_product", methods=["POST"])
def add_product():
    if 'username' not in session:
        return redirect(url_for("index"))

    try:
        name = request.form["name"]
        category_id = request.form.get("category_id")
        features = request.form["features"]
        price = request.form["price"]
        quantity = request.form.get("quantity", 1)
        image = request.files["image"]
        
        # Campos avanzados
        sku = request.form.get("sku", "").strip()
        brand = request.form.get("brand", "")
        weight = request.form.get("weight", 0)
        dimensions = request.form.get("dimensions", "")
        warranty_months = request.form.get("warranty_months", 12)
        is_featured = request.form.get("is_featured") == "on"
        is_active = request.form.get("is_active") != "off"  # Por defecto activo
        
        # Verificar si se quiere crear una nueva categoría
        new_category_name = request.form.get("new_category_name")
        if new_category_name and not category_id:
            conn = get_db_connection()
            try:
                # Verificar si la categoría ya existe
                existing_category = conn.execute("SELECT id FROM categories WHERE name = ?", (new_category_name,)).fetchone()
                if existing_category:
                    conn.close()
                    return f"La categoría '{new_category_name}' ya existe. Por favor selecciónala de la lista.", 400
                
                # Crear nueva categoría
                conn.execute("""
                    INSERT INTO categories (name, description, color, icon, is_active, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    new_category_name,
                    request.form.get("new_category_description", ""),
                    request.form.get("new_category_color", "#123d2f"),
                    request.form.get("new_category_icon", "📦"),
                    1,  # Activa por defecto
                    datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                ))
                conn.commit()
                
                # Obtener el ID de la nueva categoría
                category_id = conn.execute("SELECT id FROM categories WHERE name = ?", (new_category_name,)).fetchone()['id']
                print(f"✅ Nueva categoría creada: {new_category_name} (ID: {category_id})")
                
            except Exception as e:
                conn.close()
                print(f"❌ Error al crear categoría: {str(e)}")
                return f"Error al crear categoría: {str(e)}", 400
            finally:
                conn.close()

        if not category_id:
            return "Debe seleccionar una categoría o crear una nueva", 400

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            return "No se subió imagen", 400

        conn = get_db_connection()
        try:
            # Si no se proporciona SKU, generar uno automáticamente
            if not sku:
                # Generar SKU basado en el nombre del producto y timestamp
                timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                sku = f"{name[:3].upper()}{timestamp}"
            
            # Verificar si el SKU ya existe
            existing_sku = conn.execute("SELECT id FROM products WHERE sku = ?", (sku,)).fetchone()
            if existing_sku:
                # Si el SKU existe, generar uno nuevo
                timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                sku = f"{name[:3].upper()}{timestamp}"
            
            # Obtener el ID del usuario actual
            user_id = get_current_user_id()
            
            conn.execute("""
                INSERT INTO products (
                    name, category_id, features, price, image_filename, quantity,
                    sku, brand, weight, dimensions, warranty_months, is_featured, is_active, created_by, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, category_id, features, price, filename, quantity,
                sku, brand, weight, dimensions, warranty_months, is_featured, is_active, user_id,
                datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            
            # Mostrar mensaje de éxito con el SKU generado
            if not request.form.get("sku"):
                print(f"✅ Producto agregado con SKU generado: {sku}")
            else:
                print(f"✅ Producto agregado: {name}")
            
        except Exception as e:
            conn.close()
            print(f"❌ Error al agregar producto: {str(e)}")
            return f"Error al agregar producto: {str(e)}", 400
        finally:
            conn.close()
        
        return redirect(url_for("index"))
        
    except Exception as e:
        print(f"❌ Error general en add_product: {str(e)}")
        return f"Error inesperado: {str(e)}", 500

# Eliminar producto (creador o admin)
@app.route("/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión para eliminar productos"}), 401
    
    conn = get_db_connection()
    try:
        # Obtener información del producto
        product = conn.execute("""
            SELECT p.*, u.username as created_by_username 
            FROM products p 
            LEFT JOIN users u ON p.created_by = u.id 
            WHERE p.id = ?
        """, (product_id,)).fetchone()
        
        if not product:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404
        
        # Verificar permisos: solo el creador o admin puede eliminar
        current_user_id = get_current_user_id()
        is_creator = product['created_by'] == current_user_id
        is_admin_user = is_admin()
        
        if not is_creator and not is_admin_user:
            return jsonify({"success": False, "message": "No tienes permisos para eliminar este producto"}), 403
        
        # Eliminar la imagen del servidor
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image_filename'])
        if os.path.exists(image_path):
            os.remove(image_path)
        
        # Eliminar el producto de la base de datos
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        
        return jsonify({
            "success": True, 
            "message": f"Producto '{product['name']}' eliminado correctamente por {'admin' if is_admin_user else 'el creador'}"
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al eliminar producto: {str(e)}"}), 500
    finally:
        conn.close()

# Obtener información de un producto para editar
@app.route("/get_product/<int:product_id>")
def get_product(product_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401
    
    conn = get_db_connection()
    try:
        # Obtener información del producto con categoría
        product = conn.execute("""
            SELECT p.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
                   u.username as created_by_username
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN users u ON p.created_by = u.id
            WHERE p.id = ?
        """, (product_id,)).fetchone()
        
        if not product:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404
        
        # Verificar permisos: solo el creador o admin puede editar
        current_user_id = get_current_user_id()
        is_creator = product['created_by'] == current_user_id
        is_admin_user = is_admin()
        
        if not is_creator and not is_admin_user:
            return jsonify({"success": False, "message": "No tienes permisos para editar este producto"}), 403
        
        # Convertir a diccionario para JSON
        product_dict = dict(product)
        
        return jsonify({
            "success": True,
            "product": product_dict
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al obtener producto: {str(e)}"}), 500
    finally:
        conn.close()

# Editar producto
@app.route("/edit_product/<int:product_id>", methods=["POST"])
def edit_product(product_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión para editar productos"}), 401
    
    try:
        name = request.form["name"]
        category_id = request.form.get("category_id")
        features = request.form["features"]
        price = request.form["price"]
        quantity = request.form.get("quantity", 1)
        
        # Campos avanzados
        sku = request.form.get("sku", "").strip()
        brand = request.form.get("brand", "")
        weight = request.form.get("weight", 0)
        dimensions = request.form.get("dimensions", "")
        warranty_months = request.form.get("warranty_months", 12)
        is_featured = request.form.get("is_featured") == "on"
        is_active = request.form.get("is_active") != "off"
        
        # Verificar si se quiere crear una nueva categoría
        new_category_name = request.form.get("new_category_name")
        if new_category_name and not category_id:
            conn = get_db_connection()
            try:
                # Verificar si la categoría ya existe
                existing_category = conn.execute("SELECT id FROM categories WHERE name = ?", (new_category_name,)).fetchone()
                if existing_category:
                    conn.close()
                    return jsonify({"success": False, "message": f"La categoría '{new_category_name}' ya existe. Por favor selecciónala de la lista."}), 400
                
                # Crear nueva categoría
                conn.execute("""
                    INSERT INTO categories (name, description, color, icon, is_active, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    new_category_name,
                    request.form.get("new_category_description", ""),
                    request.form.get("new_category_color", "#123d2f"),
                    request.form.get("new_category_icon", "📦"),
                    1,  # Activa por defecto
                    datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                ))
                conn.commit()
                
                # Obtener el ID de la nueva categoría
                category_id = conn.execute("SELECT id FROM categories WHERE name = ?", (new_category_name,)).fetchone()['id']
                print(f"✅ Nueva categoría creada: {new_category_name} (ID: {category_id})")
                
            except Exception as e:
                conn.close()
                print(f"❌ Error al crear categoría: {str(e)}")
                return jsonify({"success": False, "message": f"Error al crear categoría: {str(e)}"}), 400
            finally:
                conn.close()

        if not category_id:
            return jsonify({"success": False, "message": "Debe seleccionar una categoría o crear una nueva"}), 400

        conn = get_db_connection()
        try:
            # Verificar permisos: solo el creador o admin puede editar
            product = conn.execute("SELECT created_by FROM products WHERE id = ?", (product_id,)).fetchone()
            if not product:
                return jsonify({"success": False, "message": "Producto no encontrado"}), 404
            
            current_user_id = get_current_user_id()
            is_creator = product['created_by'] == current_user_id
            is_admin_user = is_admin()
            
            if not is_creator and not is_admin_user:
                return jsonify({"success": False, "message": "No tienes permisos para editar este producto"}), 403
            
            # Manejar nueva imagen si se subió
            image_filename = None
            if 'image' in request.files and request.files['image'].filename:
                image = request.files['image']
                if image:
                    # Eliminar imagen anterior
                    old_product = conn.execute("SELECT image_filename FROM products WHERE id = ?", (product_id,)).fetchone()
                    if old_product and old_product['image_filename']:
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], old_product['image_filename'])
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    
                    # Guardar nueva imagen
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_filename = filename
            
            # Actualizar producto
            if image_filename:
                conn.execute("""
                    UPDATE products SET 
                        name = ?, category_id = ?, features = ?, price = ?, quantity = ?,
                        sku = ?, brand = ?, weight = ?, dimensions = ?, warranty_months = ?,
                        is_featured = ?, is_active = ?, image_filename = ?
                    WHERE id = ?
                """, (
                    name, category_id, features, price, quantity,
                    sku, brand, weight, dimensions, warranty_months, is_featured, is_active,
                    image_filename, product_id
                ))
            else:
                conn.execute("""
                    UPDATE products SET 
                        name = ?, category_id = ?, features = ?, price = ?, quantity = ?,
                        sku = ?, brand = ?, weight = ?, dimensions = ?, warranty_months = ?,
                        is_featured = ?, is_active = ?
                    WHERE id = ?
                """, (
                    name, category_id, features, price, quantity,
                    sku, brand, weight, dimensions, warranty_months, is_featured, is_active,
                    product_id
                ))
            
            conn.commit()
            print(f"✅ Producto actualizado: {name}")
            
            return jsonify({
                "success": True, 
                "message": f"Producto '{name}' actualizado correctamente"
            })
            
        except Exception as e:
            conn.close()
            print(f"❌ Error al actualizar producto: {str(e)}")
            return jsonify({"success": False, "message": f"Error al actualizar producto: {str(e)}"}), 400
        finally:
            conn.close()
        
    except Exception as e:
        print(f"❌ Error general en edit_product: {str(e)}")
        return jsonify({"success": False, "message": f"Error inesperado: {str(e)}"}), 500

# Procesar compra
@app.route("/process_purchase", methods=["POST"])
def process_purchase():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión para comprar"}), 401
    
    try:
        product_id = int(request.form.get("product_id"))
        quantity = int(request.form.get("quantity", 1))
        
        # Datos de tarjeta
        card_number = request.form.get("card_number")
        card_holder = request.form.get("card_holder")
        expiry_month = int(request.form.get("expiry_month"))
        expiry_year = int(request.form.get("expiry_year"))
        cvv = request.form.get("cvv")
        
        # Validaciones básicas
        if not all([card_number, card_holder, expiry_month, expiry_year, cvv]):
            return jsonify({"success": False, "message": "Todos los campos de tarjeta son requeridos"}), 400
        
        if len(card_number) < 13 or len(card_number) > 19:
            return jsonify({"success": False, "message": "Número de tarjeta inválido"}), 400
        
        if len(cvv) < 3 or len(cvv) > 4:
            return jsonify({"success": False, "message": "CVV inválido"}), 400
        
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        
        conn = get_db_connection()
        
        # Verificar stock disponible
        product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if not product:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404
        
        if product['quantity'] < quantity:
            return jsonify({"success": False, "message": f"Stock insuficiente. Solo hay {product['quantity']} unidades disponibles"}), 400
        
        # Calcular total
        total_amount = product['price'] * quantity
        
        # Guardar datos de tarjeta
        card_last_four = encrypt_card_data(card_number)
        conn.execute("""
            INSERT INTO user_cards (user_id, card_number, card_holder, expiry_month, expiry_year, cvv, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, card_last_four, card_holder, expiry_month, expiry_year, cvv, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Registrar transacción
        conn.execute("""
            INSERT INTO transactions (user_id, product_id, quantity, total_amount, card_last_four, transaction_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, product_id, quantity, total_amount, card_last_four, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Actualizar stock
        new_quantity = product['quantity'] - quantity
        conn.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "Compra realizada exitosamente",
            "transaction": {
                "product_name": product['name'],
                "quantity": quantity,
                "total_amount": total_amount,
                "new_stock": new_quantity
            }
        })
        
    except ValueError:
        return jsonify({"success": False, "message": "Datos inválidos"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al procesar compra: {str(e)}"}), 500

# Obtener historial de transacciones del usuario
@app.route("/transactions")
def get_transactions():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    
    conn = get_db_connection()
    transactions = conn.execute("""
        SELECT t.*, p.name as product_name, p.price as product_price
        FROM transactions t
        JOIN products p ON t.product_id = p.id
        WHERE t.user_id = ?
        ORDER BY t.transaction_date DESC
    """, (user_id,)).fetchall()
    conn.close()
    
    return jsonify({
        "success": True,
        "transactions": [dict(t) for t in transactions]
    })

# Calificar producto
@app.route("/rate_product/<int:product_id>", methods=["POST"])
def rate_product(product_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión para calificar"}), 401
    
    try:
        rating = int(request.form.get("rating"))
        comment = request.form.get("comment", "")
        
        if rating < 1 or rating > 5:
            return jsonify({"success": False, "message": "La calificación debe estar entre 1 y 5"}), 400
        
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        
        conn = get_db_connection()
        
        # Verificar si el producto existe
        product = conn.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
        if not product:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404
        
        # Insertar o actualizar la calificación
        conn.execute("""
            INSERT OR REPLACE INTO product_ratings (product_id, user_id, rating, comment, timestamp) 
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, user_id, rating, comment, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Recalcular el promedio de calificaciones
        ratings = conn.execute("SELECT rating FROM product_ratings WHERE product_id = ?", (product_id,)).fetchall()
        if ratings:
            avg_rating = sum(r['rating'] for r in ratings) / len(ratings)
            conn.execute("UPDATE products SET rating = ?, rating_count = ? WHERE id = ?", 
                        (round(avg_rating, 1), len(ratings), product_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Calificación guardada correctamente"})
        
    except ValueError:
        return jsonify({"success": False, "message": "Calificación inválida"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al guardar calificación: {str(e)}"}), 500

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

# Registro
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    
    if not username or not password:
        return jsonify({"success": False, "message": "Usuario y contraseña son requeridos"}), 400
    
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"success": True, "message": "Usuario registrado correctamente"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "El usuario ya existe"}), 409
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al registrar usuario: {str(e)}"}), 500
    finally:
        conn.close()

# Ruta para ver visitas (solo admin)
@app.route("/visitas")
def visitas():
    if not is_admin():
        return redirect(url_for("index"))
    
    conn = get_db_connection()
    visitas = conn.execute("SELECT * FROM visits ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("visitas.html", visitas=visitas)

# ================= RUTA DE BÚSQUEDA INSTANTÁNEA =================
@app.route('/buscar')
def buscar():
    q = request.args.get('q', '').strip()
    conn = get_db_connection()
    query = '''
        SELECT p.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
               u.username as created_by_username
        FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.created_by = u.id
        WHERE p.is_active = 1
    '''
    params = []
    if q:
        query += ''' AND (
            p.name LIKE ? OR
            p.features LIKE ? OR
            p.price LIKE ? OR
            c.name LIKE ? OR
            p.sku LIKE ? OR
            p.brand LIKE ?
        )'''
        like_q = f'%{q}%'
        params = [like_q, like_q, like_q, like_q, like_q, like_q]
    query += ' ORDER BY c.name, p.name'
    productos = conn.execute(query, params).fetchall()
    categorias = conn.execute('SELECT * FROM categories WHERE is_active = 1 ORDER BY name').fetchall()
    conn.close()

    # Registrar búsqueda en busquedas.db
    if q:
        import sqlite3 as sql_busq
        conn_busq = sql_busq.connect('busquedas.db')
        c_busq = conn_busq.cursor()
        c_busq.execute('SELECT id, count FROM searches WHERE term = ?', (q,))
        row = c_busq.fetchone()
        if row:
            c_busq.execute('UPDATE searches SET count = count + 1 WHERE id = ?', (row[0],))
        else:
            c_busq.execute('INSERT INTO searches (term, count) VALUES (?, 1)', (q,))
        conn_busq.commit()
        conn_busq.close()

    # Renderizar solo el bloque de productos (como en main)
    return render_template('bloque_productos.html', productos=productos, categorias=categorias)
# ==============================================================

# Ruta para ver términos de búsqueda y su cantidad, ordenados de mayor a menor concurrencia
@app.route('/busquedas')
def busquedas():
    if not is_admin():
        return 'Acceso restringido', 403
    import sqlite3 as sql_busq
    conn_busq = sql_busq.connect('busquedas.db')
    c_busq = conn_busq.cursor()
    c_busq.execute('SELECT term, count FROM searches ORDER BY count DESC, term ASC')
    resultados = c_busq.fetchall()
    conn_busq.close()
    return render_template('busquedas.html', resultados=resultados)

# Ruta para ver usuarios (solo admin)
@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if not is_admin():
        return 'Acceso restringido', 403
    conn = get_db_connection()
    msg = ''
    # Agregar usuario
    if request.method == 'POST' and 'add_user' in request.form:
        new_username = request.form.get('new_username', '').strip()
        new_password = request.form.get('new_password', '').strip()
        if new_username and new_password:
            try:
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (new_username, new_password))
                conn.commit()
                msg = f"Usuario '{new_username}' agregado correctamente."
            except sqlite3.IntegrityError:
                msg = f"El usuario '{new_username}' ya existe."
        else:
            msg = 'Usuario y contraseña requeridos.'
    # Eliminar usuario
    if request.method == 'POST' and 'delete_user' in request.form:
        del_user_id = request.form.get('delete_user_id')
        if del_user_id and del_user_id != '1':  # No permitir borrar admin
            conn.execute('DELETE FROM users WHERE id = ?', (del_user_id,))
            conn.commit()
            msg = f"Usuario eliminado correctamente."
        else:
            msg = 'No se puede eliminar el usuario admin.'
    usuarios = conn.execute('SELECT id, username, password FROM users ORDER BY id').fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios, msg=msg)

# Lanzar servidor Flask en hilo y luego iniciar tunnel
def run():
    init_db()  # Crea la tabla visits si no existe
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    thread = threading.Thread(target=run)
    thread.start()
    time.sleep(3)
    os.system("host.exe tunnel --url http://localhost:5000 --no-autoupdate")

#==================================================================================================================
"""from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
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
    app.run(debug=True)"""
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