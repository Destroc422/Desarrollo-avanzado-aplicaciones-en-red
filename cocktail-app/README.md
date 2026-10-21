# Estanco y Coctelería El Grillo

Aplicación web para consultar el menú local, descubrir recetas externas, crear cuentas, hacer pedidos con entrega programada y administrar productos y servicios adicionales.

## Tecnologías

- **Frontend:** React, Axios, Lucide y CSS adaptable.
- **API:** FastAPI bajo `/api/v1`, SQLAlchemy y SQLite.
- **Sesión:** cookie HTTP-only firmada con JWT; el navegador no guarda el token.
- **Pagos:** integración preparada para Wompi Checkout en COP; la confirmación se recibe mediante evento firmado.

## Puesta en marcha

### API

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `backend/.env` antes de iniciar: establece un `SECRET_KEY` aleatorio de al menos 32 caracteres. Configura el origen real del frontend en `FRONTEND_ORIGINS` y `FRONTEND_URL`. No publiques el archivo `.env`.

```powershell
python -m app.main
```

La API queda en `http://localhost:8000`; la documentación interactiva está en `/docs`. Las comprobaciones operativas están en `/health` y `/ready`.

### Administrador inicial

Con el servidor detenido o en otra consola, desde `backend` ejecuta:

```powershell
python -m app.bootstrap_admin
```

El programa solicita usuario y contraseña de forma interactiva. No existe una cuenta ni contraseña predeterminada. Este procedimiento puede promover una cuenta existente a administradora.

### Interfaz web

```powershell
cd frontend
npm install
npm start
```

Para una API en otro origen, define `REACT_APP_API_URL` en `frontend/.env.local` con el origen de la API. Debe coincidir con `FRONTEND_ORIGINS`; en desarrollo, usa `localhost` en ambos extremos para que la cookie de sesión se envíe con las solicitudes.

## Funciones

- Menú local con búsqueda, filtros por categoría, detalle e ingredientes con cantidades.
- Recetas externas del servicio TheCocktailDB a través de un proxy del backend.
- Registro de clientes con nombre, correo, teléfono, documento, dirección y ciudad.
- Carrito, servicios adicionales, creación y consulta de pedidos y programación de entrega.
- Panel de personal para mantener cócteles, costos de ingredientes, precios, imágenes, servicios y estados de pedido.
- Imágenes limitadas a 5 MB y formatos JPG, PNG, GIF o WebP; los archivos reciben nombres aleatorios.
- Respuestas de error uniformes, rutas versionadas, control de roles y compatibilidad con pantallas móviles.

## Datos y pagos

La aplicación crea tablas nuevas y aplica cambios aditivos al archivo SQLite existente. No borra los datos previos. Las cuentas antiguas con rol administrador pasan a cliente al aplicar la actualización; usa el comando de administrador para volver a otorgar el rol autorizado. Los cócteles antiguos sin precio válido quedan ocultos hasta que el personal los complete con un precio real.

Para habilitar Wompi, configura `WOMPI_PUBLIC_KEY`, `WOMPI_INTEGRITY_SECRET` y `WOMPI_EVENTS_SECRET` con credenciales del ambiente elegido. En producción usa HTTPS y configura en Wompi el endpoint público `https://tu-dominio/api/v1/orders/wompi-webhook`. Un retorno del navegador no confirma el pago; solo el evento firmado y validado actualiza el pedido. Sin estas credenciales, se puede elegir pago contra entrega, pero no iniciar un pago en línea.

Completa teléfono, dirección, correo e Instagram del negocio con datos reales en el archivo `.env`; la interfaz no inventa esos datos. El carrito se guarda localmente en el navegador. La cookie de sesión HTTP-only se crea al iniciar sesión o registrarse; la aplicación no utiliza cookies de analítica.

## Límites conocidos

- SQLite y migración aditiva cubren la instalación actual; aún se requiere definir migraciones versionadas y una base de datos compartida para producción.
- No se han añadido pruebas automatizadas, CI, TLS ni copias de seguridad en esta entrega.
- La integración de Wompi requiere credenciales, URL pública HTTPS y configuración de webhooks antes de aceptar pagos reales.
