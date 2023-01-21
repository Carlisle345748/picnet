import re
import subprocess
from os import listdir

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Build frontend, collect static and modify index.html template'

    def handle(self, *args, **options):
        subprocess.run(['python', 'manage.py', 'collectstatic', '--clear', '--noinput', '--verbosity', '2'])

        index_file = open("backend/templates/backend/index.html", 'r+')
        index = index_file.read()

        for file in listdir('frontend/dist/assets'):
            if file.startswith("index-") and file.endswith('js'):
                file_hash = file.split("-")[1].split(".")[0]
                index = re.sub("static 'assets/index-([a-zA-Z0-9]+)\\.js'", f"static 'assets/index-{file_hash}.js'", index)

        for file in listdir('frontend/dist/assets'):
            if file.startswith("index-") and file.endswith('css'):
                file_hash = file.split("-")[1].split(".")[0]
                index = re.sub("static 'assets/index-([a-zA-Z0-9]+)\\.css'", f"static 'assets/index-{file_hash}.css'", index)

        index_file.seek(0)
        index_file.write(index)
        index_file.close()

