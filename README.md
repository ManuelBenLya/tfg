# SMI — Sistema Centralizado de Supervisión de Infraestructuras IT

![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js&logoColor=white)
![TimescaleDB](https://img.shields.io/badge/TimescaleDB-PostgreSQL_15-fdb515?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)

Plataforma integral y escalable para la monitorización en tiempo real de servidores e infraestructura de red, bajo un modelo **SaaS B2B Multi-Tenant**. Proporciona telemetría continua de hardware, supervisión de carpetas críticas, detección de anomalías con alertas multicanal, generación de reportes ejecutivos en PDF y visualización avanzada mediante un cuadro de mando web interactivo.

---

## Índice

1. [Descripción del Proyecto](#1-descripción-del-proyecto)
2. [Características Principales](#2-características-principales)
3. [Arquitectura del Sistema y Stack Tecnológico](#3-arquitectura-del-sistema-y-stack-tecnológico)
4. [Estructura del Repositorio](#4-estructura-del-repositorio)
5. [Requisitos Previos y Consideraciones Especiales](#5-requisitos-previos-y-consideraciones-especiales)
6. [Instalación y Despliegue](#6-instalación-y-despliegue)
   - [6.1 Despliegue Rápido con Docker Compose (Recomendado)](#61-despliegue-rápido-con-docker-compose-recomendado)
   - [6.2 Despliegue Manual / Entorno de Desarrollo Local](#62-despliegue-manual--entorno-de-desarrollo-local)
     - [Base de Datos (TimescaleDB / PostgreSQL)](#a-base-de-datos)
     - [Backend (FastAPI)](#b-backend)
     - [Frontend (Next.js)](#c-frontend)
     - [Agente Recolector (Python / PyQt6)](#d-agente-recolector)
7. [Guía de Uso Rápido](#7-guía-de-uso-rápido)
   - [7.1 Creación de Empresa y Primer Administrador](#71-creación-de-empresa-y-primer-administrador)
   - [7.2 Alta de Servidores y Token de Autenticación](#72-alta-de-servidores-y-token-de-autenticación)
   - [7.3 Conexión del Agente Recolector](#73-conexión-del-agente-recolector)
   - [7.4 Cuadro de Mando y Telemetría](#74-cuadro-de-mando-y-telemetría)
   - [7.5 Configuración de Alertas y Notificaciones](#75-configuración-de-alertas-y-notificaciones)
8. [Variables de Entorno](#8-variables-de-entorno)
9. [Batería de Pruebas](#9-batería-de-pruebas)
10. [Autor](#10-autor)

---

## 1. Descripción del Proyecto

El **Sistema Centralizado de Supervisión de Infraestructuras IT (SMI)** nace como solución a la dispersión de métricas técnicas y a la falta de herramientas de monitorización ligeras y accesibles para entornos corporativos y PYMEs.

El ecosistema conecta tres capas complementarias:
1. **Agentes Ligeros de Telemetría:** Clientes multiplataforma que se ejecutan en segundo plano en los servidores a supervisar, extrayendo métricas sin penalizar el rendimiento del sistema anfitrión.
2. **Backend Centralizado:** API REST asíncrona de alto rendimiento que valida, procesa y almacena series temporales optimizadas, evaluando en milisegundos si se superan los umbrales de alerta.
3. **Frontend Web:** Panel de administración interactivo y reactivo que traduce los datos brutos en gráficas comprensibles, resúmenes de salud y herramientas de toma de decisiones.

---

## 2. Características Principales

- **Telemetría de Hardware en Tiempo Real:** Monitorización de consumo de CPU (%), uso y disponibilidad de memoria RAM (MB/GB), porcentaje general de disco, espacio libre y latencia de red hacia destinos clave mediante sondeo ICMP.
- **Supervisión de Almacenamiento Granular:** Medición del tamaño de directorios críticos del sistema operativo, motores de bases de datos y carpetas de registros (*logs*).
- **Arquitectura SaaS Multi-Tenant Estricta:** Aislamiento lógico de empresas mediante identificadores únicos (`UUID`), garantizando la privacidad de los datos entre diferentes organizaciones.
- **Control de Acceso Basado en Roles (RBAC):** Perfiles diferenciados de Administrador (gestión de servidores, empleados y SMTP) y Operador (supervisión granular de los servidores asignados).
- **Sistema de Alertas Inteligente:** Detección automática al rebasar umbrales configurables por servidor, con soporte de notificaciones multicanal:
  - Correo electrónico corporativo (configuración SMTP propia por empresa).
  - Webhooks de Discord.
  - Webhooks de Slack.
- **Agente con Bandeja del Sistema (System Tray):** Aplicación de escritorio desarrollada con PyQt6 que incluye interfaz gráfica minimalista de configuración y opción de empaquetado como ejecutable binario autónomo (`.exe` o binario ELF) mediante PyInstaller.
- **Informes Técnicos en PDF:** Generación bajo demanda de reportes consolidados del estado de los servidores para auditorías técnicas.
- **Históricos Optimizados:** Compatibilidad con *hypertables* y agregaciones continuas en TimescaleDB para consultas temporales ultra-eficientes.

---

## 3. Arquitectura del Sistema y Stack Tecnológico

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, Uvicorn, PyJWT, Passlib/Bcrypt, FPDF.
- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons, Recharts, Axios, next-themes.
- **Base de Datos:** PostgreSQL 15 con la extensión TimescaleDB para series temporales.
- **Agente de Telemetría:** Python 3.12, PyQt6, psutil, requests, PyInstaller.
- **Contenedores:** Docker y Docker Compose.

---

## 4. Estructura del Repositorio

```text
.
├── docker-compose.yml          # Orquestación de TimescaleDB, Backend y Frontend
├── backend/                    # API RESTful (FastAPI)
│   ├── app/
│   │   ├── api/                # Enrutadores (usuarios, servidores, métricas, alertas)
│   │   ├── core/               # Configuración centralizada y seguridad JWT
│   │   ├── crud/               # Operaciones de persistencia en base de datos
│   │   ├── db/                 # Sesión y configuración SQLAlchemy
│   │   ├── models/             # Modelos ORM (Empresa, Usuario, Servidor, Métrica, Alerta)
│   │   ├── schemas/            # Esquemas de validación Pydantic
│   │   └── services/           # Generación de PDF y notificaciones
│   ├── alembic/                # Historial de migraciones de base de datos
│   ├── test/                   # Suite de pruebas (lógica, seguridad, integridad, carga)
│   ├── Dockerfile              # Imagen Docker del Backend
│   └── requirements.txt        # Dependencias de Python
├── frontend/                   # Interfaz de Usuario (Next.js)
│   ├── src/
│   │   ├── app/                # Rutas y páginas (Dashboard, Servidores, Alertas, Equipo, etc.)
│   │   ├── components/         # Componentes visuales reutilizables y gráficas
│   │   └── services/           # Cliente HTTP y consumo de la API
│   ├── Dockerfile              # Imagen Docker del Frontend
│   └── package.json            # Dependencias de Node.js
└── agente/                     # Agente de monitorización de escritorio
    ├── agente.py               # Lógica de recolección y bandeja de sistema PyQt6
    └── agente.spec             # Especificación para empaquetado con PyInstaller
```

---

## 5. Requisitos Previos y Consideraciones Especiales

### Requisitos de Software
- **Docker** (versión 24.0 o superior) y **Docker Compose v2** (si se opta por despliegue en contenedores).
- **Node.js** (v20 o superior) y gestor de paquetes `npm` (para ejecución manual del frontend).
- **Python** (v3.11 o v3.12) y `pip` (para ejecución manual de backend y agente).

### Consideraciones Especiales
- **Permisos de Red e ICMP (Ping):** El agente recolector ejecuta una comprobación de latencia mediante comando `ping`. En ciertos entornos Linux protegidos puede requerirse que el usuario cuente con permisos para sockets raw (`setcap cap_net_raw+ep`).
- **Librerías de Sistema para Compilación:** En sistemas basados en Debian/Ubuntu sin Docker, se requiere instalar dependencias para compilar `psycopg2`:
  ```bash
  sudo apt-get update && sudo apt-get install -y gcc libpq-dev
  ```
- **Soporte Gráfico para el Agente:** La interfaz de configuración del agente utiliza **PyQt6**. Si se ejecuta en un servidor Linux puramente headless (sin entorno gráfico X11/Wayland), debe ejecutarse configurando las credenciales previamente o en modo servicio.

---

## 6. Instalación y Despliegue

### 6.1 Despliegue Rápido con Docker Compose (Recomendado)

La forma más rápida y reproducible de levantar todo el ecosistema (Base de datos + Backend + Frontend) es usando Docker Compose:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/ManuelBenLya/tfg.git
   cd tfg
   ```

2. **Levantar los servicios:**
   ```bash
   docker compose up --build -d
   ```

3. **Verificar el estado de los contenedores:**
   ```bash
   docker compose ps
   ```

4. **Acceso a los servicios:**
   - **Frontend (Panel Web):** [http://localhost:3000](http://localhost:3000)
   - **Backend (API REST):** [http://localhost:8000](http://localhost:8000)
   - **Documentación Interactiva Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Base de Datos TimescaleDB:** `localhost:5432`

---

### 6.2 Despliegue Manual / Entorno de Desarrollo Local

Si deseas ejecutar cada componente de forma individual para depuración o desarrollo:

#### a) Base de Datos
Inicia una instancia de TimescaleDB o PostgreSQL:
```bash
docker run -d --name db_timescale -p 5432:5432 \
  -e POSTGRES_USER=db_user \
  -e POSTGRES_PASSWORD=db_password \
  -e POSTGRES_DB=app_db \
  timescale/timescaledb:latest-pg15
```

#### b) Backend
1. Navega al directorio del backend:
   ```bash
   cd backend
   ```
2. Crea y activa un entorno virtual de Python:
   ```bash
   # En Windows
   python -m venv venv
   .\venv\Scripts\activate

   # En Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```
4. Aplica las migraciones de base de datos con Alembic:
   ```bash
   alembic upgrade head
   ```
5. Inicia el servidor de desarrollo FastAPI:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### c) Frontend
1. Navega al directorio del frontend:
   ```bash
   cd ../frontend
   ```
2. Instala las dependencias de Node:
   ```bash
   npm install
   ```
3. Inicia el servidor de desarrollo de Next.js:
   ```bash
   npm run dev
   ```
4. Abre [http://localhost:3000](http://localhost:3000) en el navegador.

#### d) Agente Recolector
1. Navega al directorio del agente:
   ```bash
   cd ../agente
   ```
2. Instala las dependencias requeridas:
   ```bash
   pip install psutil requests PyQt6
   ```
3. Ejecuta el agente:
   ```bash
   python agente.py
   ```
   *(Opcional)* Para generar el archivo ejecutable binario:
   ```bash
   pyinstaller agente.spec
   ```
   El ejecutable resultante se encontrará en la carpeta `agente/dist/`.

---

## 7. Guía de Uso Rápido

### 7.1 Creación de Empresa y Primer Administrador
La plataforma funciona bajo un modelo multi-inquilino. Para inicializar una nueva organización:
1. Emite una petición HTTP `POST` a `/api/usuarios/crear-empresa-master` pasando la cabecera `x-master-key` configurada en el sistema (por defecto: `clave-maestra-tfg-2026-secure`):
   ```bash
   curl -X POST "http://localhost:8000/api/usuarios/crear-empresa-master" \
     -H "Content-Type: application/json" \
     -H "x-master-key: clave-maestra-tfg-2026-secure" \
     -d '{
       "nombre_empresa": "Mi Empresa IT",
       "email": "admin@empresa.com",
       "password": "PasswordSegura123!"
     }'
   ```
2. Accede al panel web en [http://localhost:3000/login](http://localhost:3000/login) e inicia sesión con las credenciales registradas.

### 7.2 Alta de Servidores y Token de Autenticación
1. Una vez dentro del panel, dirígete a la sección **Servidores** y haz clic en **Añadir Servidor**.
2. Indica el nombre del servidor (p. ej. `Servidor Producción 01`) y su dirección IP.
3. Copia el **Token de Autenticación** generado. *Nota: Por motivos de seguridad criptográfica, este token se presenta en claro una única vez al crearlo.*

### 7.3 Conexión del Agente Recolector
1. Inicia el agente (`agente.py` o el binario compilado) en la máquina a monitorizar.
2. Haz clic derecho sobre el icono del agente en la bandeja del sistema (System Tray) y selecciona **Configuración**.
3. Introduce:
   - **URL del Backend:** `http://<IP_DEL_SERVIDOR_BACKEND>:8000` (o el dominio configurado).
   - **Token de Autenticación:** Pega el token generado en el paso anterior.
4. Guarda los cambios. El agente comenzará a enviar métricas automáticamente cada pocos segundos y el estado del servidor cambiará a `Online`.

### 7.4 Cuadro de Mando y Telemetría
- En la pestaña **Dashboard**, visualiza métricas consolidadas en tiempo real: evolución de CPU, uso de memoria RAM, gráficas de latencia y desglose de particiones de disco.
- Utiliza la opción **Descargar Reporte PDF** para generar un resumen técnico del estado del servidor.

### 7.5 Configuración de Alertas y Notificaciones
1. En **Servidores**, pulsa en **Configurar Umbrales** para definir los límites deseados (porcentaje máximo de CPU, RAM o disco, y milisegundos de latencia).
2. En la sección **Ajustes**, configura las vías de notificación:
   - Servidor SMTP de tu empresa para alertas por correo electrónico.
   - URLs de Webhooks de Discord o Slack para recibir avisos instantáneos en tus canales de equipo.

---

## 8. Variables de Entorno

Puedes personalizar la configuración del sistema mediante un archivo `.env` en la raíz o en el directorio `backend/`:

| Variable | Descripción | Valor por Defecto |
| :--- | :--- | :--- |
| `DATABASE_URL` | Cadena de conexión a PostgreSQL/TimescaleDB | `postgresql://db_user:db_password@localhost:5432/app_db` |
| `SECRET_KEY` | Clave secreta para la firma criptográfica de tokens JWT | *(Clave generada en config.py)* |
| `ALGORITHM` | Algoritmo de firma de tokens | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de validez del token de sesión | `30` |
| `MASTER_SECRET_KEY` | Clave maestra para el aprovisionamiento de empresas SaaS | `clave-maestra-tfg-2026-secure` |
| `NEXT_PUBLIC_API_URL` | URL de la API accesible desde el frontend | `http://localhost:8000` |

---

## 9. Pruebas

El proyecto incluye un conjunto de pruebas automatizadas con **Pytest** y pruebas de rendimiento con **Locust**:

```bash
cd backend

# Ejecución de pruebas unitarias, de lógica y seguridad
pytest test/ -v

# Ejecución de pruebas de carga con Locust
locust -f test/carga/locustfile.py --host=http://localhost:8000
```

---

## 10. Autor

- **Manuel Benítez Lyashenko**
- **María Luque Ródriguez**
- **Antonio Araúzo Azofra**
- Trabajo Fin de Grado — *Grado en Ingeniería Informática (Mención en Ingeniería del Software)*
- Escuela Politécnica Superior de Córdoba (**EPSC**), Universidad de Córdoba (**UCO**)
