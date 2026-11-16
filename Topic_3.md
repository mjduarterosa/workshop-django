# IV. Templates and Static Files (2 hours)

| Section | Topic |
|---|---|---|
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

We use a separate **playground** page so you can experiment without breaking the main pages.

### 1. Set up the playground

Add to the top of `members/views.py` (if it is not already there):

```python
from datetime import date
```

Add the view:

```python
def playground(request):
    context = {
        "name": "alice johnson",
        "number": 3,
        "books": ["Dune", "Beloved", "The Hobbit"],
        "club": {"name": "Page Turners", "city": "London"},
        "member": Member.objects.first(),
        "today": date.today(),
        "empty_list": [],
        "html": "<strong>bold text</strong>",
        "long_text": "A very long description of the next book we will read together this month.",
    }
    return render(request, "members/playground.html", context)
```

Add the route to `members/urls.py`:

```python
    path("playground/", views.playground, name="playground"),
```

Create `members/templates/members/playground.html`:

```html
{% extends "members/base.html" %}

{% block title %}Template playground{% endblock %}

{% block content %}
  <h1>Template playground</h1>

  <h2>1. Variables</h2>
  <p>Text: {{ name }}</p>
  <p>Number: {{ number }}</p>
  <p>Dictionary lookup: {{ club.name }} ({{ club.city }})</p>
  <p>List index: {{ books.0 }}</p>
  <p>Object attribute: {{ member.name }}</p>
  <p>Missing variable: [{{ does_not_exist }}]</p>

  <h2>2. Filters</h2>
  <p>{{ name|title }}</p>
  <p>{{ name|upper }}</p>
  <p>{{ long_text|truncatechars:30 }}</p>
  <p>{{ books|length }} books</p>
  <p>{{ books|join:", " }}</p>
  <p>{{ today|date:"l, j F Y" }}</p>
  <p>{{ member.favorite_book|default:"Not set" }}</p>
  <p>You have {{ number }} book{{ number|pluralize }}.</p>

  <h2>3. Tags</h2>

  {% if number > 5 %}
    <p>Big club</p>
  {% elif number > 1 %}
    <p>Medium club</p>
  {% else %}
    <p>Small club</p>
  {% endif %}

  <ul>
    {% for book in books %}
      <li>
        {{ forloop.counter }}. {{ book }}
        {% if forloop.first %}(first){% endif %}
        {% if forloop.last %}(last){% endif %}
      </li>
    {% endfor %}
  </ul>

  {% for item in empty_list %}
    <p>{{ item }}</p>
  {% empty %}
    <p>The list is empty.</p>
  {% endfor %}

  {% with first_book=books.0 %}
    <p>The first book is {{ first_book }}.</p>
  {% endwith %}

  {# A one-line comment: it will not appear in the HTML #}
  {% comment %}
    A multi-line comment.
    Nothing in here is shown either.
  {% endcomment %}

  <h2>4. Escaping</h2>
  <p>Escaped (default): {{ html }}</p>
  <p>With |safe: {{ html|safe }}</p>
{% endblock %}
```

Open `<site>/playground/`.

### 2. What you should see

**Variables**

| Template | Output | Notes |
|---|---|---|
| `{{ name }}` | alice johnson | |
| `{{ club.name }}` | Page Turners | Dictionary key |
| `{{ books.0 }}` | Dune | List index (starts at 0) |
| `{{ member.name }}` | The first member's name | Object attribute |
| `[{{ does_not_exist }}]` | `[]` | Missing variables print nothing and cause no error |

The dot (`.`) is Django's universal lookup. For `a.b` it tries a dictionary key, then an attribute, then a list index. It also calls methods (without parentheses).

**Filters**

| Template | Output |
|---|---|
| `{{ name\|title }}` | Alice Johnson |
| `{{ name\|upper }}` | ALICE JOHNSON |
| `{{ long_text\|truncatechars:30 }}` | A very long description of th… |
| `{{ books\|length }}` | 3 |
| `{{ books\|join:", " }}` | Dune, Beloved, The Hobbit |
| `{{ today\|date:"l, j F Y" }}` | Today's date, for example Monday, 16 November 2026 |
| `{{ member.favorite_book\|default:"Not set" }}` | The book, or "Not set" if empty |
| `{{ number\|pluralize }}` | `s` (and nothing when the number is 1) |

Filters can be chained: `{{ name|title|truncatechars:8 }}`.

**Tags**

| Tag | What it does |
|---|---|
| `{% if %}`, `{% elif %}`, `{% else %}` | Conditions. Supports `and`, `or`, `not`, `==`, `!=`, `<`, `>`, `in` |
| `{% for %} ... {% empty %}` | Loops. `{% empty %}` runs when the list has no items |
| `forloop.counter` | Position in the loop, starting at 1 (`counter0` starts at 0) |
| `forloop.first`, `forloop.last` | `True` on the first or last item |
| `{% with x=expression %}` | Gives an expression a short name inside the block |
| `{% url 'name' arg %}` | Builds a URL from a route name |
| `{% csrf_token %}` | Required inside every `<form method="post">` |
| `{% now "Y" %}` | Prints the current date or time |
| `{% include "file.html" %}` | Inserts another template |
| `{% extends %}` and `{% block %}` | Template inheritance |

**Escaping**

By default, Django converts characters such as `<` and `>` into harmless text. So `{{ html }}` shows the literal text `<strong>bold text</strong>`, while `{{ html|safe }}` shows **bold text**.

> **Security warning:** only use `|safe` on content you wrote yourself. If you use it on text that users typed, an attacker can inject scripts into your page (cross-site scripting, or XSS). Auto-escaping is one of Django's most important protections.

### 3. Use the syntax on the real pages

Update the home page to show the banner as formatted text. We wrote the banner ourselves in the view, so it is safe:

```html
  <p>{{ banner|safe }}</p>
```

Update `members/templates/members/member_detail.html` to use filters and conditions:

```html
{% extends "members/base.html" %}

{% block title %}{{ member.name }}{% endblock %}

{% block content %}
  <h1>{{ member.name }}</h1>

  {% if member.joined.year == 2024 %}
    <p><strong>Founding member</strong></p>
  {% endif %}

  <p>Email: {{ member.email }}</p>
  <p>Favourite book: {{ member.favorite_book|default:"Not set" }}</p>
  <p>Joined: {{ member.joined|date:"j F Y" }}</p>
  <p><a href="{% url 'members:list' %}">Back to the list</a></p>
{% endblock %}
```

Open `<site>/members/1/` (Alice joined in 2024) and `<site>/members/3/` (Carla joined in 2025). Only the first shows "Founding member".

Show the member count on the list page. Add this below the `<h1>` in `member_list.html`:

```html
  <p class="muted">{{ members|length }} member{{ members|length|pluralize }}</p>
```

### Checkpoint

- [ ] `/playground/` shows the output described in the tables
- [ ] You can explain the difference between `{{ }}` and `{% %}`
- [ ] You can explain why `|safe` should be used with care
- [ ] Only the 2024 members show "Founding member"

### Exercise

On the playground page, add a line that prints the number of books and uses `{% if %}` to say "Add more books!" when there are fewer than five.

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
│       ├── js/
│       │   └── search.js
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

### 4. JavaScript

Create `members/static/members/js/search.js`. It filters the member cards as you type:

```javascript
document.addEventListener("DOMContentLoaded", function () {
  const search = document.getElementById("member-search");
  if (!search) return;

  const cards = document.querySelectorAll("#member-list .card");

  search.addEventListener("input", function () {
    const term = search.value.toLowerCase();
    cards.forEach(function (card) {
      const matches = card.textContent.toLowerCase().includes(term);
      card.style.display = matches ? "" : "none";
    });
  });
});
```

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
    <a href="{% url 'members:add' %}">Add member</a>
  </nav>

  <main>
    {% block content %}{% endblock %}
  </main>

  <footer>
    <hr>
    <p>&copy; {% now "Y" %} Book Club Workshop</p>
  </footer>

  {% block scripts %}{% endblock %}
</body>
</html>
```

Replace the whole contents of `members/templates/members/member_list.html`. It adds a search box and loads the JavaScript for this page only:

```html
{% extends "members/base.html" %}
{% load static %}

{% block title %}Members{% endblock %}

{% block content %}
  <h1>Book Club Members</h1>
  <p class="muted">{{ members|length }} member{{ members|length|pluralize }}</p>

  <input type="search" id="member-search" placeholder="Search members...">

  <div id="member-list">
    {% for member in members %}
      {% include "members/_member_card.html" %}
    {% empty %}
      <p>No members yet.</p>
    {% endfor %}
  </div>
{% endblock %}

{% block scripts %}
  <script src="{% static 'members/js/search.js' %}"></script>
{% endblock %}
```

**Important:** `{% load static %}` is **not inherited**. Every template that uses `{% static %}` needs its own `{% load static %}`. In a child template, put it right after `{% extends %}`.

### 6. Test it

Refresh the browser with a **hard refresh** (`Ctrl+Shift+R`, or `Cmd+Shift+R` on a Mac), because browsers cache CSS files.

| Check | You should see |
|---|---|
| Any page | A dark navigation bar with a book logo and styled cards |
| `<site>/members/` | A search box. Type `al` and only Alice stays visible |
| `<site>/static/members/css/style.css` | The raw CSS text |

You can open any static file directly using `STATIC_URL` plus the file path. This is the quickest way to debug a missing file.

Now change the nav colour in `style.css` (for example `#2c3e50` to `#8e44ad`) and refresh. You edit one file and the whole site changes.

### 7. Static files in production

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
- [ ] The search box filters the member list
- [ ] You can open `/static/members/css/style.css` directly in the browser

### Exercise

Add a favicon: create a small SVG at `members/static/members/images/favicon.svg` and add this line inside `<head>` in `base.html`:

```html
<link rel="icon" href="{% static 'members/images/favicon.svg' %}">
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Invalid block tag 'static'. Did you forget to register or load this tag?` | Add `{% load static %}` to that template (after `{% extends %}`) |
| `'extends' tag must be the first tag in the template` | Move `{% extends %}` to the top. Only `{# comments #}` may come before it |
| `TemplateDoesNotExist` | Check the path `members/templates/members/<file>.html` and that `"members"` is in `INSTALLED_APPS` |
| A variable prints nothing | The name in the template does not match the key in the context dictionary. Check spelling |
| `NoReverseMatch` | The route name in `{% url %}` does not exist. Check `app_name` and the route's `name` |
| Styling does not appear | Hard refresh the page. Check the file path and that the folder is named `static` |
| `404` for `/static/...` | Check `members/static/members/css/style.css` exists exactly as written, and that `DEBUG = True` |
| JavaScript does nothing | Open the browser console (`F12`) for errors, and check the element IDs match (`member-search`, `member-list`) |
| New static file not found | Restart `runserver` once if the `static` folder was created after the server started |
| `DisallowedHost` (Codespaces) | Add the settings block from the Part II setup and restart the server |