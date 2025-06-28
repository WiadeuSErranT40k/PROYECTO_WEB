import sqlite3

conn = sqlite3.connect("busquedas.db")
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL,
    count INTEGER DEFAULT 1
)
''')
conn.commit()
conn.close()
print("Tabla 'searches' creada correctamente en busquedas.db") 