# Notas Importantes sobre Usuarios y Empresas

## Tipos de Usuarios en CotizApp

### 1. Superusuario (Django Superuser)
- **Propósito**: Administrador de la plataforma completa
- **Empresa**: No tiene empresa asignada (null)
- **Permisos**: Acceso total a todas las empresas y usuarios
- **Creación**: `python manage.py createsuperuser`
- **Uso**: Gestión de la plataforma, acceso al admin de Django

### 2. Administrador de Empresa
- **Propósito**: Administrador de una empresa específica
- **Empresa**: Debe tener empresa asignada (obligatorio)
- **Permisos**: 
  - Crear/editar/eliminar usuarios de su empresa
  - Crear/editar/eliminar productos
  - Ver/editar datos de su empresa
  - Generar reportes
- **Rol**: `ADMIN` en el campo `rol`

### 3. Empleado
- **Propósito**: Usuario operativo de una empresa
- **Empresa**: Debe tener empresa asignada (obligatorio)
- **Permisos**:
  - Ver productos
  - Crear/editar clientes
  - Crear/editar cotizaciones
  - Ver datos de la empresa
- **Rol**: `EMPLEADO` en el campo `rol`

## Flujo de Configuración Inicial

1. **Crear Superusuario** (primera vez):
   ```bash
   python manage.py createsuperuser
   ```
   - Email: admin@plataforma.com
   - No requiere empresa

2. **Crear Primera Empresa** (desde admin o API):
   - Acceder a http://localhost:8000/admin/
   - Ir a Empresas → Agregar empresa
   - Completar datos (nombre, RUT, etc.)

3. **Crear Administrador de Empresa**:
   - Desde admin o API
   - Asignar rol: ADMINISTRADOR
   - Asignar empresa creada en paso 2

4. **El Administrador puede crear Empleados**:
   - Usando la API o admin
   - Todos los empleados se asignan automáticamente a su empresa

## Diferencias Clave

| Característica | Superusuario | Admin Empresa | Empleado |
|----------------|--------------|---------------|----------|
| Empresa | null | Requerida | Requerida |
| Rol | is_superuser=True | rol=ADMIN | rol=EMPLEADO |
| Acceso Admin Django | ✅ | ❌ | ❌ |
| Ver todas las empresas | ✅ | ❌ | ❌ |
| Crear usuarios | ✅ | ✅ (solo su empresa) | ❌ |
| Editar productos | ✅ | ✅ (solo su empresa) | ❌ |
| Crear cotizaciones | ✅ | ✅ | ✅ |

## Ejemplo de Creación por API

### Crear Administrador de Empresa (como superusuario):
```bash
curl -X POST http://localhost:8000/api/usuarios/ \
  -H "Authorization: Bearer {superuser_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@empresa.com",
    "username": "admin_empresa",
    "first_name": "Juan",
    "last_name": "Pérez",
    "rol": "ADMIN",
    "empresa": 1,
    "password": "contraseña_segura",
    "confirm_password": "contraseña_segura"
  }'
```

### Crear Empleado (como admin de empresa):
```bash
curl -X POST http://localhost:8000/api/usuarios/ \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "empleado@empresa.com",
    "username": "empleado1",
    "first_name": "María",
    "last_name": "González",
    "rol": "EMPLEADO",
    "password": "contraseña_segura",
    "confirm_password": "contraseña_segura"
  }'
```
(La empresa se asigna automáticamente)
