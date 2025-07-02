
# 🚀 Ziara 

![Ziara Banner](/ziara_app/static/img/logo5.png)

---

## ✨ ¿Qué es Ziara?

**Ziara** es una plataforma web creada para optimizar la **gestión de barberías**, permitiendo administrar citas, servicios, barberos, productos e inventario, todo desde una interfaz moderna y fácil de usar.

Este proyecto es más que un código: es una muestra de mi pasión por la tecnología, el diseño de sistemas y la programación desde cero. 💻🔥

---

## 🌐 Tecnologías utilizadas

| Categoría      | Tecnología                         |
| -------------- | ---------------------------------- |
| Frontend       | HTML5 + CSS3                       |
| Backend        | Django (Python)                    |
| Base de datos  | SQLite (modo local)                |
| Despliegue     | PythonAnywhere                     |
| Automatización | Tareas programadas con `cron`      |
| Otros          | Email automático, logs, backup zip |

---

## 📁 Estructura del Proyecto

```
ZiaraX/
├── manage.py
├── ziara/                  # Configuración del proyecto
│   ├── settings.py         # Configuraciones generales (correo, apps, etc.)
│   ├── urls.py             # URLs del proyecto principal
├── ziara_app/              # Lógica de negocio
│   ├── views.py            # Controladores (vistas)
│   ├── models.py           # Modelos de la base de datos
│   ├── templates/          # Plantillas HTML
│   ├── static/             # Archivos CSS, JS e imágenes
│   └── management/commands/# Tareas automáticas (cron jobs)
├── db.sqlite3              # Base de datos local (IGNORADA por Git)
├── requirements.txt        # Dependencias del proyecto
└── README.md
```

---

## ⚙️ Cómo ejecutar Ziara en local

1. Clona el repositorio:

```bash
git clone https://github.com/holguinLab/ZiaraX.git
```

2. Entra en la carpeta del proyecto:

```bash
cd ZiaraX
```

3. Crea un entorno virtual (opcional pero recomendado):

```bash
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```

4. Instala las dependencias:

```bash
pip install -r requirements.txt
```

5. Ejecuta las migraciones:

```bash
python manage.py migrate
```

6. Corre el servidor:

```bash
python manage.py runserver
```

7. Abre el navegador en: `http://127.0.0.1:8000/`

---

## 🔐 Seguridad y Automatización

* `.gitignore` excluye `.sqlite3`, `.env`, y `logs/` para proteger tu info sensible.
* Sistema de **tareas programadas (`cron`)** envía automáticamente backups comprimidos por correo.
* Soporte para múltiples apps y modularidad.

---

## 📦 Recomendaciones

* Usa `python-dotenv` para manejar variables sensibles como claves y correos.
* Despliega en PythonAnywhere o Render para producción.
* Configura logs con `>> archivo.log 2>&1` para monitorear tareas automáticas.

---

## ✉️ Contacto

📬 **Correo del proyecto:** [holguin.pyweb@gmail.com](mailto:holguin.pyweb@gmail.com)
🌐 **Repositorio:** [https://github.com/holguinLab/ZiaraX](https://github.com/holguinLab/ZiaraX)

---

## 🌟 Este proyecto es solo el comienzo

Ziara representa más que funcionalidad: representa mi camino como desarrollador. Cada línea, cada error corregido, cada avance... todo forma parte de este viaje. ✨

> *“No importa si camino solo, porque cada línea de código me hace más fuerte.”* 💪
