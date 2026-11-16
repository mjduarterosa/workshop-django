# I. Introduction to Django (1 hour)

## A. Overview of the Django framework

See slides.

---

## B. Installing and setting up Django

Choose **one** of the two options below. GitHub Codespaces is the quickest because everything is pre-configured. Use the local option if you prefer working on your own machine.

### Option 1: GitHub Codespaces (recommended)

No installation is needed. Python, Django and the VS Code extensions are set up for you.

1. Sign in to your GitHub account.
2. Open the workshop repository: `https://github.com/mjduarterosa/workshop-django`
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

Run this in the terminal, from the root of your workspace (add a trailing `.` if you don't want to create the top project folder, only the content).

```bash
django-admin startproject book_club
```

This creates:

```
book_club/
├── manage.py
└── book_club/
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```
Now:
```
cd book_club
```
Inside you will find:

| File | Purpose |
|---|---|
| `manage.py` | Command-line tool for running and managing your project |
| `book_club/settings.py` | Project configuration |
| `book_club/urls.py` | Top-level URL routing |
| `book_club/wsgi.py`, `asgi.py` | Entry points for web servers |

### 2. Allow Codespaces URLs (Codespaces only)

Skip this step if you are working locally.

Open `book_club/settings.py`. Add `import os` at the top of the file, then replace the line `ALLOWED_HOSTS = []` with this block:

```python
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = []

if os.environ.get("CODESPACES") == "true":
    _domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    ALLOWED_HOSTS.append(f".{_domain}")
    CSRF_TRUSTED_ORIGINS.append(f"https://*.{_domain}")
```

Without this, the browser shows a `DisallowedHost` error.

### 3. Run the development server

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
python manage.py startapp members
```

This creates:

```
members/
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

In `book_club/settings.py`, add `"members"` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "members",  # <-- add this line
]
```

### 7. Write your first view

Edit `members/views.py`:

```python
from django.http import HttpResponse


def members(request):
    return HttpResponse("Hello World!")
```

### 8. Add a URL for the view

Create a new file `members/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path("members/", views.members, name="members"),
]
```

Then connect it to the project in `book_club/urls.py`:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("members.urls")),
]
```

### 9. Test it

Start the server again (use the command for your setup from step 3) and refresh the browser. You should see:

```
Hello World!
```

### Checkpoint

You have completed this section when:

- [ ] `python -m django --version` prints a version number
- [ ] The development server starts without errors
- [ ] Your browser displays "Hello World!"