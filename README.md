# Antonito Avances - Sistema de Productos

## Descripción
Sistema web para gestión de productos con categorías dinámicas, sistema de usuarios, compras y calificaciones.

## Características Implementadas

### ✅ Funcionalidades Principales
- **Gestión de Productos**: Crear, editar, eliminar y visualizar productos
- **Categorías Dinámicas**: Crear nuevas categorías al agregar productos
- **Sistema de Usuarios**: Registro, login y gestión de sesiones
- **Sistema de Compras**: Procesamiento de pagos con tarjetas
- **Calificaciones**: Sistema de estrellas y comentarios para productos
- **Historial de Compras**: Seguimiento de transacciones por usuario

### ✅ Mejoras Recientes Implementadas

#### 🔧 Corrección de Base de Datos
- **Problema resuelto**: Los productos con categorías inválidas (`category_id = "new"`) no se mostraban
- **Solución**: Se corrigieron automáticamente todos los productos con categorías inválidas
- **Campo agregado**: `created_by` para rastrear quién creó cada producto

#### 🔐 Sistema de Permisos Mejorado
- **Eliminación de productos**: 
  - ✅ El creador del producto puede eliminarlo
  - ✅ El superusuario (admin) puede eliminar cualquier producto
  - ❌ Otros usuarios no pueden eliminar productos ajenos

- **Edición de productos**:
  - ✅ El creador del producto puede editarlo
  - ✅ El superusuario (admin) puede editar cualquier producto
  - ❌ Otros usuarios no pueden editar productos ajenos

#### ✏️ Función de Edición de Productos
- **Modal de edición**: Interfaz completa para modificar productos
- **Campos editables**: Nombre, categoría, características, precio, stock, imagen, etc.
- **Opciones avanzadas**: SKU, marca, peso, dimensiones, garantía, destacado, activo
- **Nuevas categorías**: Posibilidad de crear categorías durante la edición
- **Validación de permisos**: Solo el creador o admin puede editar

#### 👤 Información del Creador
- **Visualización**: Se muestra quién creó cada producto
- **Rastreabilidad**: Información completa de autoría

#### 🎨 Mejoras de Interfaz
- **Botones de administración**: Editar y eliminar con estilos diferenciados
- **Responsive design**: Adaptación para dispositivos móviles
- **Feedback visual**: Confirmaciones y mensajes de error mejorados

## Usuarios del Sistema

### Superusuario (Admin)
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Permisos**: 
  - Crear, editar y eliminar cualquier producto
  - Ver estadísticas de visitas
  - Acceso completo al sistema

### Usuarios Regulares
- **Registro**: Libre para cualquier usuario
- **Permisos**:
  - Crear productos (se asocian automáticamente a su cuenta)
  - Editar y eliminar solo sus propios productos
  - Comprar productos
  - Calificar productos
  - Ver su historial de compras

## Estructura de Base de Datos

### Tablas Principales
- **users**: Usuarios del sistema
- **categories**: Categorías de productos
- **products**: Productos con información completa
- **transactions**: Historial de compras
- **product_ratings**: Calificaciones de productos
- **visits**: Estadísticas de visitas
- **user_cards**: Datos de tarjetas (encriptados)

### Campos Nuevos en Products
- `created_by`: ID del usuario que creó el producto
- `sku`: Código único del producto (se genera automáticamente)
- `brand`: Marca del producto
- `weight`: Peso en kg
- `dimensions`: Dimensiones del producto
- `warranty_months`: Meses de garantía
- `is_featured`: Producto destacado
- `is_active`: Estado activo/inactivo

## Instalación y Uso

### Requisitos
- Python 3.7+
- Flask
- SQLite3

### Configuración
1. Clonar el repositorio
2. Instalar dependencias: `pip install flask`
3. Ejecutar la base de datos: `python bd.py`
4. Iniciar el servidor: `python app.py`

### Acceso
- **URL local**: http://localhost:5000
- **Admin**: admin / admin123
- **Registro**: Libre para nuevos usuarios

## Características Técnicas

### Seguridad
- Validación de permisos por producto
- Encriptación básica de datos de tarjeta
- Protección contra acceso no autorizado

### Rendimiento
- Consultas SQL optimizadas
- Índices en campos críticos
- Manejo eficiente de imágenes

### Escalabilidad
- Estructura modular
- Separación de responsabilidades
- Base de datos normalizada

## Estado del Proyecto
✅ **Completado**: Todas las funcionalidades solicitadas implementadas
✅ **Probado**: Sistema funcional y estable
✅ **Documentado**: Código comentado y README actualizado

## Próximas Mejoras Sugeridas
- Sistema de notificaciones
- Filtros avanzados de productos
- Sistema de cupones y descuentos
- Panel de administración más completo
- API REST para integración externa 