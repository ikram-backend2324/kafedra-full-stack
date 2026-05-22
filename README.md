# Kafedra Hújjetlerin Elektron Basqarıw Sisteması

**Electronic Department Document Management System**  
*Developer: Duysenbaeva Umida*

---

## Stack

| Layer       | Technology                                      |
|-------------|------------------------------------------------|
| Backend     | Django 4.x + SQLite                            |
| Frontend    | Tailwind CSS (CDN) + Animate.css               |
| AI          | OpenRouter → `google/gemini-2.0-flash`         |
| Languages   | Uzbek (`uz`, default) & Karakalpak (`kaa`)     |
| Auth        | Django built-in auth                           |

---

## Quick Start

```bash
# 1. Create & activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Bootstrap everything in one command
bash setup.sh

# 3. Add your OpenRouter API key in .env
#    OPENROUTER_API_KEY=sk-or-v1-...

# 4. Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** — log in with `admin` / your password.

---

## Project Structure

```
kafedra/
├── core/
│   ├── settings.py       # All config, reads from .env
│   ├── urls.py           # Root URL routing
│   └── wsgi.py
├── documents/
│   ├── models.py         # Document model
│   ├── views.py          # Dashboard, Upload, Detail, Analyze
│   ├── forms.py          # DocumentUploadForm
│   ├── utils.py          # OpenRouter / Gemini API helper
│   ├── urls.py
│   └── admin.py
├── templates/
│   ├── base.html         # App shell (sidebar + navbar)
│   ├── dashboard.html    # Document list
│   ├── login.html
│   └── documents/
│       ├── upload.html
│       └── detail.html
├── locale/
│   ├── uz/LC_MESSAGES/django.po
│   └── kaa/LC_MESSAGES/django.po
├── media/                # Uploaded files (git-ignored)
├── .env.example          # Copy to .env and fill in secrets
├── requirements.txt
└── manage.py
```

---

## Environment Variables (`.env`)

| Variable             | Required | Description                        |
|----------------------|----------|------------------------------------|
| `SECRET_KEY`         | ✅       | Django secret key                  |
| `DEBUG`              | —        | `True` for dev, `False` in prod    |
| `ALLOWED_HOSTS`      | —        | Comma-separated hosts              |
| `OPENROUTER_API_KEY` | ✅       | Get from https://openrouter.ai/keys |

---

## AI Integration

The **Analyze** button on the document detail page sends a `POST /documents/<id>/analyze/` (AJAX) request.  
`documents/utils.py` → `analyze_document()`:

1. Reads `OPENROUTER_API_KEY` from the environment.
2. Detects the active session language (`request.LANGUAGE_CODE`).
3. Injects a language-specific system prompt so Gemini replies **exclusively** in Uzbek or Karakalpak Latin script.
4. Calls `https://openrouter.ai/api/v1/chat/completions` with model `google/gemini-2.0-flash`.
5. Saves the result to `Document.ai_summary` and returns it as JSON.

---

## Language Switching

The sidebar contains a **UZ / QQ** toggle. It submits Django's built-in `set_language` view (`/i18n/set_lang/`), which sets a cookie (`kafedra_lang`) and reloads the current page. The `LocaleMiddleware` picks up the cookie on every subsequent request.

To add or update translations:
```bash
python manage.py makemessages -l kaa   # extract strings
# ... edit locale/kaa/LC_MESSAGES/django.po
python manage.py compilemessages       # compile .mo files
```

---

## Django Admin

Access at `/admin/` — customised headers:
- **Site header**: Kafedra Hújjetlerin Elektron Basqarıw Sisteması Admin Panel
- **Site title**: Kafedra Admin
- **Index title**: Boshqaruv Paneli
