# III. Templates and Static Files (2 hours)

| Section | Topic |
|---|---|
| A | Overview of Django templates | 
| B | Creating and using template files | 
| C | Templating language and syntax | 
| D | Serving static files (CSS, JavaScript, images) | 

This part continues the **Book Club** project from the previous part (project `book_club`, app `members`).

---

## Setup

You need the finished project from Part II: the `members` app with the `Member` model, the sample members, and the templates `base.html`, `home.html`, `member_list.html` and `member_detail.html`.

---

## A. Overview of Django templates

A **template** is a text file (usually HTML) with placeholders and simple logic. A **view** gathers the data and a **template** decides how it looks.

```
Request  →  URL pattern  →  View  →  render(request, "template.html", context)  →  HTML response
                                          ↑                  ↑
                                   template file       dictionary of data
```

Django's template language (DTL) has four building blocks:

| Syntax | Name | Example | Purpose |
|---|---|---|---|
| `{{ ... }}` | Variable | `{{ member.name }}` | Print a value |
| `{{ value\|filter }}` | Filter | `{{ name\|upper }}` | Change how a value is shown |
| `{% ... %}` | Tag | `{% for m in members %}` | Logic and control flow |
| `{# ... #}` | Comment | `{# note #}` | Notes that never reach the browser |

**Where Django looks for templates.** In `book_club/settings.py` the `TEMPLATES` setting contains `"APP_DIRS": True`. This tells Django to search a `templates` folder inside every app listed in `INSTALLED_APPS`. That is why our files live at:

```
members/
└── templates/
    └── members/
        ├── base.html
        ├── home.html
        ├── member_list.html
        └── member_detail.html
```

The inner `members` folder is deliberate. It keeps template names unique across apps, so a template is always referred to as `"members/home.html"`.

### Try it

Open `members/templates/members/home.html` and look at it. It uses `{% extends %}`, two `{% block %}` tags and a `{% url %}` tag. By the end of this part you will understand every symbol in it.

---

## B. Creating and using template files

### 1. Template inheritance

`base.html` holds the layout that every page shares. Each page extends it and fills in the blocks. We now add two more blocks so pages can add their own extras.

Edit `members/templates/members/base.html`:

- Add `{% block extra_head %}{% endblock %}` just before `</head>`.
- Add `{% block scripts %}{% endblock %}` just before `</body>`.
- Change the footer text to show the current year with the `now` tag.

```html
  {% block extra_head %}{% endblock %}
</head>
```

```html
  <footer>
    <hr>
    <p>&copy; {% now "Y" %} Book Club</p>
  </footer>

  {% block scripts %}{% endblock %}
</body>
```

Rules for inheritance:

- `{% extends "members/base.html" %}` must be the **first tag** in the child template.
- Anything outside a `{% block %}` in a child template is ignored.
- A block you do not override keeps the base template's content.

### 2. Pass data from the view

Update `home` in `members/views.py`:

```python
def home(request):
    context = {
        "club_name": "Page Turners",
        "member_count": Member.objects.count(),
        "banner": "<em>Next meeting: the first Friday of the month</em>.",
    }
    return render(request, "members/home.html", context)
```

### 3. Pass data to template`

Replace the contents of `members/templates/members/home.html`:

```html
{% extends "members/base.html" %}

{% block title %}Home{% endblock %}

{% block content %}
  <h1>Welcome to {{ club_name }}!</h1>
  <p>{{ banner }}</p>
  <p>We have {{ member_count }} member{{ member_count|pluralize }}.</p>

  <p><a href="{% url 'members:list' %}">See all members</a></p>
{% endblock %}
```

### 4. Test it

| Open this URL | You should see |
|---|---|
| `<site>/` | "Welcome to Page Turners!", the member count |

You will notice the banner shows the literal text `<em>Next meeting...</em>` with the tags visible. This is **auto-escaping**, and we explain it in Section C.

### Exercise (advanced)

Create a partial `members/_footer.html`, move the `<footer>` markup from `base.html` into it, and use `{% include "members/_footer.html" %}` in `base.html`.

---

## C. Templating language and syntax

Check the following links for more information on the Django Template Language: https://docs.djangoproject.com/en/6.1/ref/templates/language/
And a cheatsheet: https://www.codecademy.com/learn/templates-in-django/modules/django-templates/cheatsheet

### 2. Escaping

By default, Django converts characters such as `<` and `>` into harmless text. So `{{ html }}` shows the literal text `<strong>bold text</strong>`, while `{{ html|safe }}` shows **bold text**.

> **Security warning:** only use `|safe` on content you wrote yourself. If you use it on text that users typed, an attacker can inject scripts into your page (cross-site scripting, or XSS). Auto-escaping is one of Django's most important protections.

### 3. Use the syntax on the real pages

Update the home page to show the banner as formatted text. We wrote the banner ourselves in the view, so it is safe:

```html
  <p>{{ banner|safe }}</p>
```
---

## D. Serving static files (CSS, JavaScript, images)

**Static files** are files that do not change per request: CSS, JavaScript and images. Django serves them separately from templates.

### 1. How static files work

`book_club/settings.py` already contains what we need. Check that you can find both lines:

```python
INSTALLED_APPS = [
    ...
    "django.contrib.staticfiles",   # the static files app
    ...
]

STATIC_URL = "static/"              # the URL prefix for static files
```

While `DEBUG = True`, `runserver` serves static files automatically from each app's `static` folder.

Create these folders and files:

```
members/
├── static/
│   └── members/
│       ├── css/
│       │   └── style.css
│       └── images/
│           └── logo.svg
└── templates/
    └── members/
        └── ...
```

As with templates, the inner `members` folder keeps file names unique across apps.

### 2. CSS

Create `members/static/members/css/style.css`:

```css
body {
  font-family: system-ui, sans-serif;
  line-height: 1.6;
  margin: 0;
  color: #222;
  background: #fafafa;
}

nav {
  background: #2c3e50;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

nav a {
  color: #fff;
  text-decoration: none;
}

nav a:hover {
  text-decoration: underline;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: bold;
}

.logo {
  width: 28px;
  height: 28px;
}

main {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1.5rem;
}

footer {
  max-width: 800px;
  margin: 3rem auto 2rem;
  padding: 0 1.5rem;
  color: #777;
  font-size: 0.9rem;
}

.card {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.card h3 {
  margin: 0 0 0.25rem;
}

.muted {
  color: #777;
  font-size: 0.9rem;
}

input[type="search"] {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
  box-sizing: border-box;
}
```

### 3. An image

Create `members/static/members/images/logo.svg` (an SVG is a text file, so you can paste it):

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
</svg>
```

To use your own picture later (for example a `.png` or `.jpg`), save it in the `images` folder and reference it the same way.

### 5. Connect the files to the templates

Replace the whole contents of `members/templates/members/base.html`. The inline `<style>` block is gone, and the page now loads the CSS file and the logo with the `static` tag:

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Home{% endblock %} | Book Club</title>
  <link rel="stylesheet" href="{% static 'members/css/style.css' %}">
  {% block extra_head %}{% endblock %}
</head>
<body>
  <nav>
    <a href="{% url 'members:home' %}" class="brand">
      <img src="{% static 'members/images/logo.svg' %}" alt="" class="logo">
      Book Club
    </a>
    <a href="{% url 'members:list' %}">Members</a>
    <a href="{% url 'members:about' %}">About</a>
  </nav>

  <main>
    {% block content %}{% endblock %}
  </main>

  <footer>
    <hr>
    <p>&copy; {% now "Y" %} Book Club</p>
  </footer>

  {% block scripts %}{% endblock %}
</body>
</html>
```

**Important:** `{% load static %}` is **not inherited**. Every template that uses `{% static %}` needs its own `{% load static %}`. In a child template, put it right after `{% extends %}`.

### 6. Test it

Refresh the browser with a **hard refresh** (`Ctrl+Shift+R`, or `Cmd+Shift+R` on a Mac), because browsers cache CSS files.

Now change the nav colour in `style.css` (for example `#2c3e50` to `#8e44ad`) and refresh. You edit one file and the whole site changes.

### 7. Bonus: Using Bootstrap 

Bootstrap is a popular CSS and JavaScript toolkit with ready-made navigation bars, cards, buttons and a responsive grid. You do not need to install anything. Load it from a CDN (a public server) with two lines in base.html. This needs an internet connection.

1. Load Bootstrap in `base.html`.

Add the CSS inside `<head>`, before your own style.css so your rules can override it:

html
```
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'members/css/style.css' %}">
```

Add the JavaScript just before {% block scripts %}:

html
```
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  {% block scripts %}{% endblock %}
```

Check getbootstrap.com for the latest version number if you want to update 5.3.3.

2. Use Bootstrap classes

Bootstrap works by adding classes to your HTML. Replace the `<nav>` and `<main>` parts of base.html:

html
```
  <nav class="navbar navbar-expand-md navbar-dark bg-dark">
    <div class="container">
      <a class="navbar-brand d-flex align-items-center gap-2" href="{% url 'members:home' %}">
        <img src="{% static 'members/images/logo.svg' %}" alt="" width="28" height="28">
        Book Club
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#main-nav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="main-nav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item"><a class="nav-link" href="{% url 'members:list' %}">Members</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'members:about' %}">About</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'members:add' %}">Add member</a></li>
        </ul>
      </div>
    </div>
  </nav>

  <main class="container my-4">
    {% block content %}{% endblock %}
  </main>
```

### 8. Static files in production (ignore)

The development server only serves static files while `DEBUG = True`. A real site collects them into one folder that a web server serves.

Add to `book_club/settings.py`:

```python
STATIC_ROOT = BASE_DIR / "staticfiles"
```

Then run:

```bash
python manage.py collectstatic
```

This copies every static file into `staticfiles/`. That folder is already ignored in the `.gitignore` we created, because it is generated and does not belong in version control. Tools such as WhiteNoise or a web server like Nginx then serve it. You do not need this to complete the workshop.

### Checkpoint

- [ ] The site has the new styling on every page
- [ ] The logo appears in the navigation bar
- [ ] You can open `/static/members/css/style.css` directly in the browser

### Exercise

Add a favicon: create a small SVG at `members/static/members/images/favicon.svg` and add this line inside `<head>` in `base.html`:

```html
<link rel="icon" href="{% static 'members/images/favicon.svg' %}">
```
