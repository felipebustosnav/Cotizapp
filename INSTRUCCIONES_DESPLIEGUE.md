# 🚀 Guía de Inicio y Despliegue - CotizApp

Este documento detalla cómo levantar todos los servicios necesarios para que la aplicación funcione, tanto en tu entorno de desarrollo local como las recomendaciones para un servidor de producción.

---

## 💻 1. Entorno de Desarrollo (Tu PC Actual)

Para que el sistema funcione completo (incluyendo el envío de correos en segundo plano), necesitas tener **4 terminales** corriendo simultáneamente.

### Terminal 1: Broker de Mensajería (Redis)
Es necesario para que Celery funcione. En tu caso, corre dentro de WSL (Ubuntu).

```bash
# Inicia el contenedor si ya existe
wsl docker start cotizapp-redis

# Si no existiera o se borró, lo creas con:
# wsl docker run -d -p 6379:6379 --name cotizapp-redis redis:alpine
```

### Terminal 2: Servidor Backend (Django)
La API principal que maneja los datos y la lógica.

```powershell
# Asegúrate de activar tu entorno virtual primero
.\venv\Scripts\Activate.ps1

# Inicia el servidor
python manage.py runserver
```

### Terminal 3: Worker de Tareas (Celery)
El encargado de enviar los correos electrónicos sin congelar la aplicación.

```powershell
# Activa el entorno virtual
.\venv\Scripts\Activate.ps1

# Inicia el worker (Nota: --pool=solo es vital en Windows)
celery -A cotizapp worker --pool=solo -l info
```

### Terminal 4: Frontend (React)
La interfaz visual de la aplicación.

```powershell
# Entra a la carpeta del frontend
cd frontend

# Inicia la aplicación (debería abrirse el navegador)
npm start
```

---

## 🌍 2. Despliegue en Producción (Cómo debería ser realmente)

En un entorno real (un servidor Linux en la nube como AWS, DigitalOcean, Azure), **NO** se usa `runserver` ni `npm start`. La arquitectura cambia para ser robusta y segura:

### Backend (Django + Gunicorn)
En lugar de `python manage.py runserver` (que es inseguro y lento para producción), se utiliza un **Servidor de Aplicaciones WSGI** como **Gunicorn**.
*   **Comando:** `gunicorn cotizapp.wsgi:application --bind 0.0.0.0:8000`
*   **Gestión:** Se usa **Systemd** o **Supervisor** para que si el servicio falla, se reinicie automáticamente.

### Frontend (React -> Archivos Estáticos)
No se corre Node.js en producción para servir React. Se "construye" la aplicación.
*   **Comando:** `npm run build`
*   Esto genera una carpeta `build/` con archivos HTML, CSS y JS optimizados y minificados. Estos archivos son servidos por un servidor web simple (Nginx).

### Servidor Web (Nginx)
Se coloca **Nginx** como la puerta de entrada principal (Reverse Proxy).
*   Recibe las peticiones del usuario.
*   Si piden la web -> Entrega los archivos estáticos de React (`build/`).
*   Si piden `/api/...` -> Redirige la petición internamente a Gunicorn (Django).
*   Maneja los certificados SSL (HTTPS).

### Docker Compose (La forma moderna)
En lugar de manejar 4 terminales o servicios sueltos, se crea un archivo `docker-compose.yml` que define todo el stack.

**Ejemplo conceptual de docker-compose.yml:**
```yaml
version: '3.8'
services:
  db:
    image: mysql:8.0
  redis:
    image: redis:alpine
  backend:
    build: .
    command: gunicorn cotizapp.wsgi:application --bind 0.0.0.0:8000
    depends_on: [db, redis]
  celery:
    build: .
    command: celery -A cotizapp worker -l info
    depends_on: [redis]
  frontend:
    build: ./frontend
    # Nginx sirviendo el build de React
```

### Resumen de Diferencias

| Característica | Desarrollo (Actual) | Producción (Ideal) |
| host | `localhost` | `midominio.com` (HTTPS) |
| Servidor App | `runserver` (Django) | `Gunicorn` + `Systemd` |
| Frontend | `npm start` (Servidor Dev) | `Nginx` sirviendo estáticos (`npm run build`) |
| Base de Datos | MySQL Local | AWS RDS o MySQL Gestionado |
| Debug | `DEBUG=True` (Muestra errores) | `DEBUG=False` (Seguro) |
