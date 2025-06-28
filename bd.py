#==================================================================================================================    
import sqlite3
from datetime import datetime

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

# Crear tabla de categorías
c.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    color TEXT DEFAULT '#123d2f',
    icon TEXT DEFAULT '📦',
    created_date TEXT,
    is_active BOOLEAN DEFAULT 1
)
''')

# Crear tabla de productos (actualizada con campo created_by)
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    features TEXT NOT NULL,
    price REAL NOT NULL,
    image_filename TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    rating REAL DEFAULT 0.0,
    rating_count INTEGER DEFAULT 0,
    sku TEXT UNIQUE,
    brand TEXT,
    weight REAL,
    dimensions TEXT,
    warranty_months INTEGER DEFAULT 12,
    is_featured BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_date TEXT,
    created_by INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
)
''')

# Crear tabla de visitas
c.execute('''
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    user_agent TEXT,
    timestamp TEXT
)
''')

# Crear tabla de evaluaciones de productos
c.execute('''
CREATE TABLE IF NOT EXISTS product_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    timestamp TEXT,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE(product_id, user_id)
)
''')

# Crear tabla de transacciones de compra
c.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    card_last_four TEXT NOT NULL,
    transaction_date TEXT,
    status TEXT DEFAULT 'completed',
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
)
''')

# Crear tabla de datos de tarjeta (encriptados en producción)
c.execute('''
CREATE TABLE IF NOT EXISTS user_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    card_number TEXT NOT NULL,
    card_holder TEXT NOT NULL,
    expiry_month INTEGER NOT NULL,
    expiry_year INTEGER NOT NULL,
    cvv TEXT NOT NULL,
    is_default BOOLEAN DEFAULT 0,
    created_date TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)
''')

# Agregar columna created_by si no existe
try:
    c.execute("ALTER TABLE products ADD COLUMN created_by INTEGER")
    print("✅ Columna created_by agregada a la tabla products")
except sqlite3.OperationalError:
    print("ℹ️ La columna created_by ya existe")

# Insertar categorías de ejemplo
categorias_ejemplo = [
    ("Electrónicos", "Productos electrónicos y tecnología", "#2e7d32", "💻"),
    ("Móviles", "Smartphones y accesorios móviles", "#1976d2", "📱"),
    ("Audio", "Auriculares, altavoces y equipos de audio", "#7b1fa2", "🎧"),
    ("Gaming", "Productos para videojuegos", "#d32f2f", "🎮"),
    ("Hogar", "Productos para el hogar", "#f57c00", "🏠"),
    ("Deportes", "Equipos y accesorios deportivos", "#388e3c", "⚽"),
    ("Moda", "Ropa y accesorios de moda", "#c2185b", "👕"),
    ("Libros", "Libros y material educativo", "#5d4037", "📚")
]

for categoria in categorias_ejemplo:
    c.execute("INSERT OR IGNORE INTO categories (name, description, color, icon, created_date) VALUES (?, ?, ?, ?, ?)", 
              (categoria[0], categoria[1], categoria[2], categoria[3], datetime.now().isoformat()))

# Insertar algunos datos de ejemplo (opcional)
# Usuario de ejemplo
c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))

# Obtener IDs de categorías
c.execute("SELECT id FROM categories WHERE name = 'Electrónicos'")
result = c.fetchone()
cat_electronicos = result[0] if result else 1

c.execute("SELECT id FROM categories WHERE name = 'Móviles'")
result = c.fetchone()
cat_moviles = result[0] if result else 2

c.execute("SELECT id FROM categories WHERE name = 'Audio'")
result = c.fetchone()
cat_audio = result[0] if result else 3

# Obtener ID del usuario admin
c.execute("SELECT id FROM users WHERE username = 'admin'")
admin_user = c.fetchone()
admin_id = admin_user[0] if admin_user else 1

# Productos de ejemplo con nuevos campos
productos_ejemplo = [
    ("Laptop Gaming", cat_electronicos, "Procesador i7, 16GB RAM, SSD 512GB", 1299.99, "laptop.jpg", 5, 4.2, 8, "LAP001", "GamingPro", 2.5, "35x25x2 cm", 24, 1, admin_id),
    ("Smartphone", cat_moviles, "Pantalla 6.1\", 128GB, Cámara 48MP", 599.99, "smartphone.jpg", 12, 4.5, 15, "PHN001", "TechMobile", 0.18, "15x7x0.8 cm", 12, 1, admin_id),
    ("Auriculares", cat_audio, "Bluetooth, Cancelación de ruido", 89.99, "auriculares.jpg", 8, 3.8, 6, "AUD001", "SoundMax", 0.25, "18x15x8 cm", 12, 0, admin_id),
    ("Mouse Gaming", cat_electronicos, "RGB, 16000 DPI, 6 botones", 45.99, "mouse.jpg", 15, 4.1, 12, "MOU001", "GamingPro", 0.12, "12x6x4 cm", 12, 0, admin_id),
    ("Tablet", cat_moviles, "Pantalla 10.1\", 64GB, WiFi", 299.99, "tablet.jpg", 6, 4.3, 9, "TAB001", "TechMobile", 0.48, "25x17x0.8 cm", 12, 1, admin_id),
    ("Altavoz Bluetooth", cat_audio, "360° sonido, 20W, Resistente al agua", 79.99, "altavoz.jpg", 10, 4.0, 7, "SPK001", "SoundMax", 0.85, "8x8x8 cm", 12, 0, admin_id)
]

for producto in productos_ejemplo:
    c.execute("INSERT OR IGNORE INTO products (name, category_id, features, price, image_filename, quantity, rating, rating_count, sku, brand, weight, dimensions, warranty_months, is_featured, created_by, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
              (producto[0], producto[1], producto[2], producto[3], producto[4], producto[5], producto[6], producto[7], producto[8], producto[9], producto[10], producto[11], producto[12], producto[13], producto[14], datetime.now().isoformat()))

# Corregir productos con category_id inválido
print("🔧 Corrigiendo productos con categorías inválidas...")
c.execute("UPDATE products SET category_id = ? WHERE category_id = 'new' OR category_id NOT IN (SELECT id FROM categories)", (cat_electronicos,))
c.execute("UPDATE products SET created_by = ? WHERE created_by IS NULL", (admin_id,))

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print("✅ Base de datos 'antonito.db' actualizada exitosamente!")
print("📊 Tablas creadas:")
print("   - users (usuarios)")
print("   - categories (categorías de productos)")
print("   - products (productos con categorías dinámicas y creador)")
print("   - visits (visitas)")
print("   - product_ratings (evaluaciones de productos)")
print("   - transactions (transacciones de compra)")
print("   - user_cards (datos de tarjeta)")
print("🔑 Usuario de ejemplo: admin / admin123")
print("📂 Categorías creadas: Electrónicos, Móviles, Audio, Gaming, Hogar, Deportes, Moda, Libros")
print("📦 Productos de ejemplo agregados con categorías y campos avanzados")
print("💳 Sistema de pagos implementado")
print("🔧 Productos con categorías inválidas corregidos")

# ===================== BASE DE DATOS DE BÚSQUEDAS =====================
import sqlite3 as sql_busq

conn_busq = sql_busq.connect("busquedas.db")
c_busq = conn_busq.cursor()
c_busq.execute('''
CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL,
    count INTEGER DEFAULT 1
)
''')
conn_busq.commit()
conn_busq.close()
# ======================================================================
#==================================================================================================================