# VII. Deployment and Production (2 hours)

| Section | Topic |
|---|---|
| A | Overview of Django deployment options | 
| B | Deploying Django to a production server | 
| C | Configuring Django for production use | 
| D | Best practices for deploying and maintaining a Django application | 

In this part we use **PythonAnywhere**, a beginner-friendly host with a free tier.

---

## A. Overview of Django deployment options

| Option | Good for | Effort |
|---|---|---|
| **PythonAnywhere** | Learning, small projects | Low |
| **Render / Railway / Heroku-style PaaS** | Small to medium apps | Low to medium |
| **VPS (DigitalOcean, Hetzner)** | Full control | High |
| **Docker + cloud (AWS, GCP, Azure)** | Large or team projects | High |

A production setup usually has: a **web server** (Gunicorn or uWSGI) running Django, a **reverse proxy** (Nginx) serving static files, and a **real database** (PostgreSQL) instead of SQLite. PythonAnywhere handles the web server and proxy for you.

---

## B. Deploying Django to a production server

**1. Push your code to GitHub or GitLab**, then sign up at pythonanywhere.com.

**2. Get your code.** Open a **Bash console** from the Dashboard:

```bash
git clone https://github.com/YOURNAME/YOURREPO.git
cd YOURREPO
```

**3. Create a virtualenv and install requirements:**

```bash
mkvirtualenv myenv --python=python3.12
pip install -r requirements.txt
```

(Make sure `requirements.txt` exists: run `pip freeze > requirements.txt` locally first.)

**4. Create the web app.** Web tab → **Add a new web app** → **Manual configuration** → pick your Python version.

On the Web tab, set:
- **Source code:** `/home/YOURUSERNAME/YOURREPO`
- **Virtualenv:** `/home/YOURUSERNAME/.virtualenvs/myenv`

**5. Edit the WSGI file** (link on the Web tab). Replace its contents with:

```python
import os
import sys

path = "/home/YOURUSERNAME/YOURREPO"
if path not in sys.path:
    sys.path.append(path)

os.environ["DJANGO_SETTINGS_MODULE"] = "yourproject.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**6. Create the database and admin user** in the Bash console:

```bash
python manage.py migrate
python manage.py createsuperuser
```

**7. Click Reload** on the Web tab and visit `YOURUSERNAME.pythonanywhere.com`.

**Task:** Deploy your project and open it in a browser.

---

## C. Configuring Django for production use

In `settings.py`:

```python
import os

DEBUG = False
ALLOWED_HOSTS = ["YOURUSERNAME.pythonanywhere.com"]
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-key")

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
```

- **`DEBUG = False`** hides detailed error pages from visitors.
- **`ALLOWED_HOSTS`** must list your domain, or Django returns a 400 error.
- **`SECRET_KEY`** should come from an environment variable, never be committed to git.

**Serve static files.** In the Bash console:

```bash
python manage.py collectstatic
```

Then on the Web tab, under **Static files**, add:
- URL: `/static/`
- Directory: `/home/YOURUSERNAME/YOURREPO/staticfiles`

Set the secret key by adding this line to the top of your WSGI file:

```python
os.environ["DJANGO_SECRET_KEY"] = "put-a-long-random-string-here"
```

If you need to generate a new key use the following command in the bash terminal:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Reload the app after any change.

**Task:** Turn `DEBUG` off, run `collectstatic`, and confirm the admin page still has its styling.

---

## D. Best practices for deploying and maintaining a Django application

- **Run the deployment check:** `python manage.py check --deploy` lists security warnings to fix.
- **Never commit secrets or `db.sqlite3`.** Add both to `.gitignore`.
- **Back up your data regularly:**
  ```bash
  python manage.py dumpdata > backup.json
  ```
- **Update your code safely:** in the Bash console, run `git pull`, then `pip install -r requirements.txt` if packages changed, then `python manage.py migrate`, `python manage.py collectstatic`, and **Reload**.
- **Check logs** when something breaks: Web tab → **Error log** and **Server log**.
- **Use HTTPS.** PythonAnywhere provides it for `*.pythonanywhere.com` domains.
- **For real projects,** move from SQLite to PostgreSQL or MySQL, and keep dependencies pinned in `requirements.txt`.

PythonAnywhere's free tier has limits (such as restricted outbound internet access and a requirement to periodically extend the app), so check their help pages for current details.

**Task:** Run `python manage.py check --deploy` and fix one warning.

---

## Quick checklist

- [ ] Code on GitHub/GitLab, `requirements.txt` present
- [ ] App deployed and reachable in the browser
- [ ] `DEBUG = False`, `ALLOWED_HOSTS` set, secret key kept out of git
- [ ] Static files collected and mapped
- [ ] A backup made with `dumpdata`
