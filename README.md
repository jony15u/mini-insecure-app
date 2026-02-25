# Mini Insecure App (Proyecto Final - Aplicaciones Seguras)

Aplicación mínima vulnerable desplegada en **DigitalOcean App Platform** para demostrar:
- Análisis estático (SAST)
- CI/CD
- Despliegue en la nube
- Centralización de logs y alertas (Better Stack)
- Prueba controlada (login fallidos y errores 500)

## Arquitectura (alto nivel)
Usuario → DigitalOcean App Platform (FastAPI) → Logs → Better Stack (Telemetry)

## Endpoints
- `GET /` interfaz web con botones para generar eventos
- `POST /login` autenticación (vulnerable a SQL Injection a propósito)
- `GET /boom` fuerza un error 500 (Internal Server Error)

## Credenciales
- Usuario: `admin`
- Password: `admin`

## Vulnerabilidades intencionales (para SAST / OWASP)
- **SQL Injection**: consulta SQL construida con f-string en `/login`
- **Credenciales hardcoded**: usuario/clave por defecto `admin/admin`
- **Falla controlada 500**: endpoint `/boom` genera excepción

## Variables de entorno (se configuran en DigitalOcean, NO en el repo)
- `BETTERSTACK_TOKEN`: token del source de Better Stack
- `BETTERSTACK_ENDPOINT`: endpoint HTTPS del source (ej: `https://...betterstackdata.com`)

> Se usan variables de entorno para **gestión de secretos** y evitar exponer credenciales en el repositorio.

## Ejecutar local (opcional)
```bash
pip install -r requirements.txt
uvicorn main:app --reload
