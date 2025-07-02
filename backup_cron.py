import os, sys, time
from pathlib import Path
from ziara_app.utils import *


# /home/holguinLab/.virtualenvs/ziara_django_puro/bin/python3.10 /home/holguinLab/ZiaraX/backup_cron.py >> /home/holguinLab/logs/backup.log 2>&1


# Configuración del proyecto Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append("/home/holguinLab/ZiaraX")  # Ruta real a tu proyecto
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ziara.settings")

import django
django.setup()



file_to_compress = '/home/holguinLab/ZiaraX/db.sqlite3'
zip_archive_name = '/home/tu_usuario/ziara/db.sqlite3.zip'

compress_file_to_zip(file_to_compress, zip_archive_name)
time.sleep(2)

# Correo
from django.core.mail import EmailMessage

subject = "Backup automático de Ziara"
body = "Adjunto respaldo diario de la base de datos de Ziara."
to_emails = ['holguin.pyweb@gmail.com']

file_path = zip_archive_name
if os.path.exists(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()

    email = EmailMessage(subject, body, to=to_emails)
    email.attach('db.sqlite3.zip', content, 'application/zip')
    email.send()
    print("Correo enviado ✅")
else:
    print("Archivo ZIP no encontrado ❌")
