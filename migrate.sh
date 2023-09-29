pip install -r requirements.txt

python3 manage.py migrate
python3 manage.py algolia_applysettings
python3 manage.py algolia_reindex