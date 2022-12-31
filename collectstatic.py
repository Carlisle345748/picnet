from os import listdir
import re
import subprocess

subprocess.run(['python', 'manage.py', 'collectstatic', '--clear', '--noinput'])

index_file = open("template/index.html", 'r+')
index = index_file.read()

for file in listdir('frontend/build/static/js'):
    if file.startswith("main") and file.endswith('js'):
        file_hash = file.split(".")[1]
        index = re.sub("static 'js/main\\.([a-zA-Z0-9]+)\\.js'", f"static 'js/main.{file_hash}.js'", index)

for file in listdir('frontend/build/static/css'):
    if file.startswith("main") and file.endswith('css'):
        file_hash = file.split(".")[1]
        index = re.sub("static 'css/main\\.([a-zA-Z0-9]+)\\.css'", f"static 'css/main.{file_hash}.css'", index)

index_file.seek(0)
index_file.write(index)
index_file.close()


