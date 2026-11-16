# workshop-django
Workshop de Introdução ao Django

# I. Introduction to Django (1 hour)

## A. Overview of the Django framework

See slides.

---

## B. Installing and setting up Django

Choose **one** of the two options below. GitHub Codespaces is the quickest because everything is pre-configured. Use the local option if you prefer working on your own machine.

### Option 1: GitHub Codespaces (recommended)

No installation is needed. Python, Django and the VS Code extensions are set up for you.

1. Sign in to your GitHub account.
2. Open the workshop repository: `https://github.com/<your-instructor>/<repo-name>`
3. Click the green **Code** button, open the **Codespaces** tab, then click **Create codespace on main**.
4. Wait about a minute while the environment builds. VS Code opens in your browser.
5. Open the terminal in VS Code (**Terminal → New Terminal**) and check that Django is installed:

   ```bash
   python -m django --version
   ```

   You should see a version number such as `5.2.x`.

> **Notes**
> - You do **not** need a virtual environment in Codespaces.
> - You do **not** need to fork the repository. If you want to save your work, commit and push, and GitHub will offer to create a fork for you.
> - Free GitHub accounts include a monthly Codespaces allowance. Stop your codespace when you finish (**Codespaces: Stop Current Codespace** in the Command Palette).

### Option 2: Local installation

**Requirements:** Python 3.10 or newer and a code editor such as VS Code.

1. Check your Python version:

   ```bash
   python --version      # on macOS/Linux you may need: python3 --version
   ```

   If Python is missing, install it from [python.org/downloads](https://www.python.org/downloads/).

2. Create a project folder and move into it:

   ```bash
   mkdir django-workshop
   cd django-workshop
   ```

3. Create a virtual environment:

   ```bash
   python -m venv .venv  # on macOS/Linux you may need: python3 -m venv .venv
   ```

4. Activate it:

   | System | Command |
   |---|---|
   | macOS / Linux | `source .venv/bin/activate` |
   | Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
   | Windows (Command Prompt) | `.venv\Scripts\activate.bat` |

   Your prompt should now start with `(.venv)`.

   > On Windows PowerShell, if activation is blocked, run
   > `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

5. Install Django:

   ```bash
   pip install --upgrade pip
   pip install "Django~=5.2"
   ```

6. Verify the installation:

   ```bash
   python -m django --version
   ```

> Remember to activate the virtual environment (step 4) each time you open a new terminal.

### Checkpoint

You are ready to continue when `python -m django --version` prints a version number.

---

## C. Creating a Django project and application

### 1. Create the project

Run this in the terminal, from the root of your workspace. The trailing `.` is important: it creates the project in the current folder instead of an extra nested one.

```bash
django-admin startproject mysite .
```

This creates:

```
.
├── manage.py
└── mysite/
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

| File | Purpose |
|---|---|
| `manage.py` | Command-line tool for running and managing your project |
| `mysite/settings.py` | Project configuration |
| `mysite/urls.py` | Top-level URL routing |
| `mysite/wsgi.py`, `asgi.py` | Entry points for web servers |

### 2. Allow Codespaces URLs (Codespaces only)

Skip this step if you are working locally.

Open `mysite/settings.py`. Add `import os` at the top of the file, then replace the line `ALLOWED_HOSTS = []` with this block:

```python
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = []

if os.environ.get("CODESPACES") == "true":
    _domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    ALLOWED_HOSTS.append(f".{_domain}")
    CSRF_TRUSTED_ORIGINS.append(f"https://*.{_domain}")
```

Without this, the browser shows a `DisallowedHost` error.

### 3. Apply the initial migrations

```bash
python manage.py migrate
```

This creates the default SQLite database (`db.sqlite3`) and Django's built-in tables.

### 4. Run the development server

**Codespaces:**

```bash
python manage.py runserver 0.0.0.0:8000
```

Click **Open in Browser** in the pop-up, or open the **Ports** tab and click the globe icon next to port 8000.

**Local:**

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

You should see Django's "The install worked successfully! Congratulations!" page. Press `Ctrl+C` in the terminal to stop the server.

### 5. Create an application

A Django *project* is made up of one or more *apps*. Each app does one job.

```bash
python manage.py startapp pages
```

This creates:

```
pages/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
│   └── __init__.py
├── models.py
├── tests.py
└── views.py
```

### 6. Register the app

In `mysite/settings.py`, add `"pages"` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pages",  # <-- add this line
]
```

### 7. Write your first view

Edit `pages/views.py`:

```python
from django.http import HttpResponse


def home(request):
    return HttpResponse("Hello, Django!")
```

### 8. Add a URL for the view

Create a new file `pages/urls.py`:

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
]
```

Then connect it to the project in `mysite/urls.py`:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
]
```

### 9. Test it

Start the server again (use the command for your setup from step 4) and refresh the browser. You should see:

```
Hello, Django!
```

### Checkpoint

You have completed this section when:

- [ ] `python -m django --version` prints a version number
- [ ] The development server starts without errors
- [ ] Your browser displays "Hello, Django!"

### Troubleshooting

| Problem | Fix |
|---|---|
| `DisallowedHost` error (Codespaces) | Add the settings block from step 2 and restart the server |
| Port 8000 missing from the Ports tab | Start the server with `0.0.0.0:8000` |
| `django-admin: command not found` (local) | Activate your virtual environment, then check Django is installed with `pip list` |
| `ModuleNotFoundError: No module named 'pages'` | Check that you ran `startapp` from the folder containing `manage.py` |
| `Page not found (404)` | Check that `pages/urls.py` exists and that `mysite/urls.py` includes it |
| `Error: That port is already in use` | Stop the other server with `Ctrl+C`, or use another port: `python manage.py runserver 8001` |