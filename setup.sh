#!/usr/bin/env bash
# ============================================================
# Kafedra — one-command bootstrap
# Usage: bash setup.sh
# ============================================================
set -e

echo "📦  Installing Python dependencies…"
pip install -r requirements.txt

echo "📋  Copying .env.example → .env (edit it to add your API key)"
[ -f .env ] || cp .env.example .env

echo "🗄️   Running database migrations…"
python manage.py makemigrations documents
python manage.py migrate

echo "🌍  Compiling translations…"
python manage.py compilemessages 2>/dev/null || true

echo "👤  Creating superuser (follow the prompts)…"
python manage.py createsuperuser --noinput \
  --username admin \
  --email admin@kafedra.uz 2>/dev/null || true
echo "   (Superuser 'admin' created; set password with: python manage.py changepassword admin)"

echo ""
echo "✅  Setup complete!"
echo "   Run the development server:  python manage.py runserver"
echo "   Open in browser:             http://127.0.0.1:8000/"
echo ""
echo "⚠️   Don't forget to add your OPENROUTER_API_KEY in .env"
