export FLASK_APP=auth_ms.app.py
export FLASK_DEBUG=1
export FLASK_ENV=development

sudo ufw allow 5000
gunicorn --bind 0.0.0.0:5000 wsgi:app

