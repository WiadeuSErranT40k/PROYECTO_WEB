#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar productos de ejemplo en categorías vacías
"""

import sqlite3
from datetime import datetime

def agregar_productos_ejemplo():
    conn = sqlite3.connect('antonito.db')
    cursor = conn.cursor()
    
    # Obtener categorías vacías
    cursor.execute("""
        SELECT c.id, c.name 
        FROM categories c 
        LEFT JOIN products p ON c.id = p.category_id 
        WHERE p.id IS NULL AND c.is_active = 1
    """)
    categorias_vacias = cursor.fetchall()
    
    print(f"📂 Categorías vacías encontradas: {len(categorias_vacias)}")
    
    # Obtener ID del usuario admin
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    admin_id = cursor.fetchone()[0]
    
    # Productos de ejemplo para cada categoría vacía
    productos_ejemplo = {
        'Gaming': [
            ('Consola Gaming Pro', 'Procesador de última generación, 4K, 1TB SSD', 599.99, 'inicio_celu_4.png'),
            ('Teclado Mecánico RGB', 'Switches Cherry MX, RGB personalizable, teclas anti-ghosting', 89.99, 'Copilot_20250624_231959.png')
        ],
        'Hogar': [
            ('Aspiradora Robot', 'Navegación inteligente, mapeo de habitaciones, control por app', 299.99, 'inicio_celu_4.png'),
            ('Cafetera Automática', 'Molino integrado, 15 bares de presión, espumador de leche', 199.99, 'Copilot_20250624_231959.png')
        ],
        'Deportes': [
            ('Bicicleta de Spinning', 'Resistencia magnética, asiento ajustable, monitor de ritmo', 399.99, 'inicio_celu_4.png'),
            ('Pesas Ajustables', '5-25kg ajustables, agarre ergonómico, material duradero', 149.99, 'Copilot_20250624_231959.png')
        ],
        'Moda': [
            ('Zapatillas Running', 'Suela de goma, amortiguación avanzada, transpirable', 129.99, 'inicio_celu_4.png'),
            ('Reloj Deportivo', 'GPS integrado, monitor cardíaco, resistente al agua', 249.99, 'Copilot_20250624_231959.png')
        ],
        'Libros': [
            ('Libro de Programación', 'Python avanzado, 500 páginas, ejemplos prácticos', 49.99, 'inicio_celu_4.png'),
            ('Novela Bestseller', 'Ficción contemporánea, 300 páginas, tapa dura', 24.99, 'Copilot_20250624_231959.png')
        ]
    }
    
    productos_agregados = 0
    
    for cat_id, cat_name in categorias_vacias:
        if cat_name in productos_ejemplo:
            print(f"📦 Agregando productos a categoría: {cat_name}")
            
            for nombre, descripcion, precio, imagen in productos_ejemplo[cat_name]:
                # Generar SKU
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                sku = f"{nombre[:3].upper()}{timestamp}"
                
                try:
                    cursor.execute("""
                        INSERT INTO products (
                            name, category_id, features, price, image_filename, quantity,
                            sku, brand, weight, dimensions, warranty_months, is_featured, is_active, created_by, created_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        nombre, cat_id, descripcion, precio, imagen, 10,
                        sku, "Marca Ejemplo", 1.0, "20x15x10 cm", 12, 0, 1, admin_id,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    productos_agregados += 1
                    print(f"   ✅ {nombre}")
                except Exception as e:
                    print(f"   ❌ Error al agregar {nombre}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Productos agregados: {productos_agregados}")
    print("✅ Base de datos actualizada correctamente!")

if __name__ == "__main__":
    agregar_productos_ejemplo() 