import os, sys, time
from pathlib import Path
from datetime import datetime
from ziara_app.utils import compress_file_to_zip # Asegúrate de tener esta función

# ✅ Configuración de Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append("/home/holguinLab/ZiaraX")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ziara.settings")

import django
django.setup()

# ✅ Nombre del archivo con fecha
fecha = datetime.now().strftime("%Y-%m-%d_%H-%M")
nombre_zip = f"backup_ziara_{fecha}.zip"

file_to_compress = '/home/holguinLab/ZiaraX/db.sqlite3'
zip_archive_name = f'/home/holguinLab/ZiaraX/{nombre_zip}'

# ✅ Comprimir base de datos
try:
    compress_file_to_zip(file_to_compress, zip_archive_name)
    print(f"📦 Backup generado: {zip_archive_name}")
except Exception as e:
    print(f"❌ Error al comprimir archivo: {e}")
    sys.exit(1)

time.sleep(2)

# ✅ Envío de correo
from django.core.mail import EmailMessage

subject = "📁 Backup automático de Ziara"
body = f"Adjunto el respaldo automático generado el {fecha}."
to_emails = ['holguin.pyweb@gmail.com']

if os.path.exists(zip_archive_name):
    try:
        with open(zip_archive_name, 'rb') as f:
            content = f.read()

        email = EmailMessage(subject, body, to=to_emails)
        email.attach(nombre_zip, content, 'application/zip')
        email.send()
        print("✉️ Correo enviado correctamente ✅")
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")
else:
    print("⚠️ No se encontró el archivo ZIP.")
