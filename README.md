# CotizApp - API REST para Sistema de Cotizaciones

API REST desarrollada con Django REST Framework para gestión de cotizaciones para PYMEs.

## Características

- ✅ Gestión de usuarios con roles (Administrador/Empleado)
- ✅ Mantenedor de empresas
- ✅ Mantenedor de productos (sin stock, solo activo/inactivo)
- ✅ Mantenedor de clientes con validación de RUT chileno
- ✅ Sistema de cotizaciones con generación de PDF
- ✅ Autenticación JWT
- ✅ Permisos basados en roles
- ✅ Documentación interactiva con Swagger
- ✅ Filtrado y búsqueda en todos los endpoints

## Requisitos Previos

- Python 3.10+
- MySQL 8.0+
- pip

## Instalación

### 1. Clonar el repositorio o descargar los archivos

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar base de datos MySQL

Ejecutar el script `create_database.sql` en MySQL:

```bash
mysql -u root -p < create_database.sql
```

O manualmente en MySQL Workbench:
```sql
CREATE DATABASE IF NOT EXISTS cotizapp_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

### 6. Configurar variables de entorno

Editar el archivo `.env` con tus credenciales de MySQL:

```env
DB_NAME=cotizapp_db
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306
```

### 7. Ejecutar migraciones

```bash
python manage.py migrate
```

### 8. Crear superusuario

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear el primer usuario administrador.

### 9. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

La API estará disponible en: `http://localhost:8000`

## Documentación de la API

Una vez que el servidor esté corriendo, puedes acceder a:

- **Swagger UI (Documentación Interactiva):** http://localhost:8000/api/docs/
- **Schema JSON:** http://localhost:8000/api/schema/
- **Panel de Administración:** http://localhost:8000/admin/

## Endpoints Principales

### Autenticación
- `POST /api/auth/login/` - Obtener token JWT
- `POST /api/auth/refresh/` - Refrescar token

### Usuarios
- `GET /api/usuarios/` - Listar usuarios
- `POST /api/usuarios/` - Crear usuario (solo admin)
- `GET /api/usuarios/me/` - Perfil del usuario actual
- `PUT /api/usuarios/{id}/` - Actualizar usuario (solo admin)
- `DELETE /api/usuarios/{id}/` - Desactivar usuario (solo admin)

### Empresa
- `GET /api/empresa/mi_empresa/` - Ver datos de la empresa
- `PUT /api/empresa/{id}/` - Actualizar empresa (solo admin)

### Productos
- `GET /api/productos/` - Listar productos
- `POST /api/productos/` - Crear producto (solo admin)
- `GET /api/productos/{id}/` - Detalle de producto
- `PUT /api/productos/{id}/` - Actualizar producto (solo admin)
- `DELETE /api/productos/{id}/` - Desactivar producto (solo admin)

### Clientes
- `GET /api/clientes/` - Listar clientes
- `POST /api/clientes/` - Crear cliente
- `GET /api/clientes/{id}/` - Detalle de cliente
- `GET /api/clientes/{id}/cotizaciones/` - Historial de cotizaciones
- `PUT /api/clientes/{id}/` - Actualizar cliente
- `DELETE /api/clientes/{id}/` - Eliminar cliente (solo admin)

### Cotizaciones
- `GET /api/cotizaciones/` - Listar cotizaciones
- `POST /api/cotizaciones/` - Crear cotización
- `GET /api/cotizaciones/{id}/` - Detalle de cotización
- `GET /api/cotizaciones/{id}/pdf/` - Descargar PDF
- `POST /api/cotizaciones/{id}/enviar/` - Enviar por email
- `PUT /api/cotizaciones/{id}/` - Actualizar cotización
- `DELETE /api/cotizaciones/{id}/` - Eliminar cotización (solo admin)

## Ejemplo de Uso

### 1. Obtener Token JWT

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@empresa.com",
    "password": "tu_contraseña"
  }'
```

Respuesta:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Crear un Producto

```bash
curl -X POST http://localhost:8000/api/productos/ \
  -H "Authorization: Bearer {tu_access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Producto Ejemplo",
    "tipo": "Servicio",
    "marca": "Marca X",
    "precio": "10000",
    "impuesto": "19",
    "activo": true
  }'
```

### 3. Crear una Cotización

```bash
curl -X POST http://localhost:8000/api/cotizaciones/ \
  -H "Authorization: Bearer {tu_access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": 1,
    "estado": "BORRADOR",
    "detalles": [
      {
        "producto": 1,
        "cantidad": 2,
        "precio_unitario": "10000",
        "impuesto": "19"
      }
    ]
  }'
```

## Estructura del Proyecto

```
cotizapp/
├── cotizapp/           # Configuración del proyecto
├── usuarios/           # App de usuarios y autenticación
├── empresas/           # App de empresas
├── productos/          # App de productos
├── clientes/           # App de clientes
├── cotizaciones/       # App de cotizaciones
│   └── utils/          # Utilidades (generador de PDF)
├── reportes/           # App de reportes (futuro)
├── media/              # Archivos subidos (logos, PDFs)
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

## Tecnologías Utilizadas

- **Django 5.0** - Framework web
- **Django REST Framework 3.14** - API REST
- **MySQL** - Base de datos
- **JWT** - Autenticación
- **ReportLab** - Generación de PDFs
- **Swagger/OpenAPI** - Documentación de API

## Seguridad

- Contraseñas hasheadas con PBKDF2
- Autenticación JWT con tokens de expiración
- Permisos basados en roles
- Validación de datos en todos los endpoints
- CORS configurado para desarrollo

## Próximos Pasos

- [ ] Implementar reportes avanzados
- [ ] Integración con WhatsApp para envío de cotizaciones
- [ ] Sistema de mensajería automática programada
- [ ] Endpoint público de autoatención
- [ ] Tests automatizados
- [ ] Despliegue en producción

## Soporte

Para reportar problemas o sugerencias, contactar al equipo de desarrollo.

## Licencia

Proyecto académico - INACAP 2025
