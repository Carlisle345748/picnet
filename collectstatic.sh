conda activate photoshare

python manage.py collectstatic --clear --noinput
cp ../frontend/build/index.html template/index.html
cp ../frontend/build/{asset-manifest.json,manifest.json,robots.txt} static/
