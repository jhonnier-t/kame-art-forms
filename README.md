# KameArt — Backend

API REST construida con **FastAPI** y **Python 3.12** que recibe formularios de consentimiento informado, valida los datos y los almacena en **Google Drive**.

---

## Stack

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.12 | Runtime |
| FastAPI | 0.115.12 | Framework API |
| Uvicorn | 0.34.0 | Servidor ASGI |
| Pydantic | 2.11.1 | Validación de datos |
| pydantic-settings | 2.8.1 | Variables de entorno |
| google-api-python-client | 2.118.0 | Google Drive API |
| google-auth-oauthlib | 1.2.0 | OAuth2 |
| python-multipart | 0.0.20 | Form data |

---

## Estructura

```
backend/
├── app/
│   ├── api/routes/
│   │   └── consent.py        # Endpoints /api/consent
│   ├── core/
│   │   └── config.py         # Variables de entorno (pydantic-settings)
│   ├── models/
│   │   └── consent.py        # Modelos Pydantic (request/response)
│   ├── services/
│   │   ├── consent_service.py # Lógica de negocio
│   │   └── drive_service.py   # Integración Google Drive
│   └── main.py               # App FastAPI + CORS + rutas
├── .env                      # Secretos (NO subir a git)
├── .env.example              # Plantilla de variables
├── get_refresh_token.py      # Script para obtener OAuth2 refresh token
└── requirements.txt
```

---

## Instalación local

### 1. Crear entorno virtual con Python 3.12

```bash
py -3.12 -m venv .venv
```

### 2. Activar el entorno

**Windows CMD:**
```cmd
.venv\Scripts\activate
```

**O usar directamente:**
```cmd
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Instalar dependencias

```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar `.env.example` → `.env` y rellenar los valores:

```env
APP_NAME=KameArt Consent Form API
DEBUG=True
CORS_ORIGINS=["http://localhost:5173"]

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
GOOGLE_DRIVE_FOLDER_ID=
```

### 5. Obtener el refresh token de Google (solo una vez)

```bash
.venv\Scripts\python.exe get_refresh_token.py
```

Se abrirá el navegador para autorizar con tu cuenta de Google. Al terminar, copia el `GOOGLE_REFRESH_TOKEN` impreso en la terminal y pégalo en `.env`.

> **Requisitos previos para el script:**
> - Proyecto en [Google Cloud Console](https://console.cloud.google.com) con **Google Drive API** habilitada
> - Credencial OAuth2 de tipo **Aplicación de escritorio**
> - Tu email agregado como **usuario de prueba** en la pantalla de consentimiento OAuth

### 6. Levantar el servidor

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Servidor disponible en: `http://localhost:8000`

---

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Redirige a `/api/consent` |
| `GET` | `/api/consent` | Estado del servicio |
| `POST` | `/api/consent/submit` | Enviar formulario de consentimiento |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI (solo `DEBUG=True`) |

### POST /api/consent/submit

**Body:**
```json
{
  "personal_data": {
    "full_name": "Juan García López",
    "document_type": "CC",
    "document_id": "12345678",
    "date_of_birth": "1990-01-15",
    "email": "juan@example.com",
    "phone": "3001234567",
    "address": "Calle 10 # 20-30",
    "city": "Bogotá",
    "emergency_contact_name": "María García",
    "emergency_contact_phone": "3007654321"
  },
  "consent_data": {
    "has_read_information": true,
    "consents_to_procedure": true,
    "authorizes_data_processing": true,
    "authorizes_media": false,
    "place": "Bogotá",
    "signature_date": "2026-03-07"
  },
  "signature_image": "data:image/png;base64,..."
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Consentimiento informado registrado exitosamente.",
  "reference_number": "A1B2C3D4",
  "drive_signature_id": "1xYz..."
}
```

---

## Almacenamiento en Google Drive

Por cada formulario enviado se crea:

```
📁 Carpeta raíz (GOOGLE_DRIVE_FOLDER_ID)
  └── 📁 Juan_Garcia_Lopez_12345678/
        ├── Juan_Garcia_Lopez_12345678_firma_20260307_143022.png
        └── Juan_Garcia_Lopez_12345678_consentimiento_20260307_143022.json
```

---

## Despliegue en Railway

1. Subir el proyecto a GitHub (`.env` está en `.gitignore`)
2. En [railway.app](https://railway.app) → **New Project → Deploy from GitHub repo**
3. Seleccionar el repositorio → configurar **Root Directory:** `backend`
4. En **Variables** agregar:
   ```
   GOOGLE_CLIENT_ID
   GOOGLE_CLIENT_SECRET
   GOOGLE_REFRESH_TOKEN
   GOOGLE_DRIVE_FOLDER_ID
   DEBUG=False
   CORS_ORIGINS=["https://tu-frontend.vercel.app"]
   ```
5. Railway detecta automáticamente el `requirements.txt` y despliega

**Start command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
``` — KameArt Consent Form API

FastAPI backend que recibe el formulario de consentimiento y almacena los datos en Google Drive.

## Inicio rápido

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows — use source .venv/bin/activate en Unix
pip install -r requirements.txt
copy .env.example .env        # Edita GOOGLE_DRIVE_FOLDER_ID
uvicorn app.main:app --reload --port 8000
```

## Endpoint principal

```
POST /api/consent/submit
Content-Type: application/json

{
  "personal_data": { ... },
  "consent_data": { ... },
  "signature_image": "<base64 PNG>"
}
```

Responde con `201 Created` y el número de referencia generado.
