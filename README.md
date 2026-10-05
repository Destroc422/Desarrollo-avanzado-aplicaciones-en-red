# 🍹 Estanco El Grillo - Cocktail App

Sistema profesional de gestión de coctelería con catálogo público y panel de administración protegido.

## 🚀 Tecnologías Utilizadas

- **Backend**: FastAPI, SQLAlchemy, SQLite, JWT (Jose), Passlib.
- **Frontend**: React, Axios, Lucide-React, CSS3 (Modern UI).

## 🛠️ Instalación y Configuración

### Backend
1. Navega a la carpeta del backend:
   `cd backend`
2. Crea un entorno virtual:
   `python -m venv venv`
3. Activa el entorno virtual:
   - Windows: `.\venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instala las dependencias:
   `pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart`
5. Ejecuta el servidor:
   `python -m app.main`

### Frontend
1. Navega a la carpeta del frontend:
   `cd frontend`
2. Instala las dependencias:
   `npm install`
3. Inicia la aplicación:
   `npm start`

## 🛡️ Seguridad y Administración

El panel de administración está protegido mediante tokens JWT. 

1. **Crear Administrador**: Utiliza la documentación de API en `http://localhost:8000/docs` para crear el primer usuario mediante el endpoint `POST /users/`.
2. **Acceso**: Haz clic en el icono de engranaje $\text{⚙️}$ en la barra de navegación del frontend y loguéate con tus credenciales.

## 📦 Características Implementadas
- [x] CRUD Completo de Cócteles.
- [x] Autenticación JWT y Hashing de Contraseñas.
- [x] Subida de imágenes locales.
- [x] Paginación y Filtrado en el Backend.
- [x] Interfaz de Usuario Responsiva y Moderna.
- [x] Manejo Global de Errores.
