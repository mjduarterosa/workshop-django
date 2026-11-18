# VI. Advanced Django Features (2 hours)

| Section | Topic |
|---|---|
| A | Django middleware and how it works | 
| B | Customizing authentication and authorization | 
| C | Working with Django signals and Celery tasks | 
| D | Using Django's caching framework | 

Examples use the `Member` and `ReadingLog` models from your project.

---

## A. Django middleware and how it works

Middleware is code that runs on every request and response, before and after your views. To illustrate how middleware works, create the following file with the class:

```python
# members/middleware.py
class SimpleLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Request: {request.method} {request.path}")   # before the view
        response = self.get_response(request)
        print(f"Response status: {response.status_code}")    # after the view
        return response
```

Register it in `settings.py`:

```python
MIDDLEWARE = [
    # ... existing middleware ...
    "members.middleware.SimpleLogMiddleware",
]
```

- Middleware runs top to bottom on the way in, and bottom to top on the way out.

Add the middleware, run the server, open a page, and watch the terminal output.

**Exercise:** add middleware functionality to allow only admin or an authorised user to access the site by logging in.

---

## B. Customizing authentication and authorization

Instead of requiring a log in to the entire site, we would like to add a log in to certain views. For example:

**Require login for a view:**

```python
from django.contrib.auth.decorators import login_required

@login_required
def add_member(request):
    ...
```
For class views include a mixin to get the same behaviour, for example:

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class MemberListView(LoginRequiredMixin,, ListView):
    model = Member
    ...

class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member
    ...
```

Set where users get sent to log in and log out:

```python
# settings.py
LOGIN_URL = "/members/login/"
LOGIN_REDIRECT_URL = "/members/"   # where to go after logging in
LOGOUT_REDIRECT_URL = "/members/login/"
```

**Require a permission:**

Instead of any user being able to log in and add a new member we might want to grant only authorised users the option of adding a new member. To do this, add the following decorator instead:

```python
from django.contrib.auth.decorators import permission_required

@login_required
@permission_required("members.add_member", raise_exception=True)
def add_member(request):
    ...
```

**Check in a template:**

Now add the log in and log out button to the base template and also the new log in template.

Create a new html template inside the templates folder in a new `registration` folder:

```html
{% extends "members/base.html" %}

{% block content %}
  <h1>Log in</h1>

  {% if form.errors %}
    <p>Your username and password didn't match. Please try again.</p>
  {% endif %}

  <form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Log in</button>
  </form>
{% endblock %}
```

Add to `members/base.html`, the new nav bar (part of it replaces what was already there):

```html
  <nav>
    <a href="{% url 'members:home' %}" class="brand">
      <img src="{% static 'members/images/logo.svg' %}" alt="" class="logo">
      Book Club
    </a>
    <a href="{% url 'members:list' %}">Members</a>
    <a href="{% url 'members:about' %}">About</a>
    {% if user.is_authenticated %}
        <span style="color: white;">Hello, {{ user.username }}</span>
        <form method="post" action="{% url 'logout' %}" style="display:inline;">
        {% csrf_token %}
        <button type="submit">Log out</button>
        </form>
    {% else %}
        <a href="{% url 'login' %}">Log in</a>
    {% endif %} 
  </nav>
```

Finally, add the authentication url to the project `urls.py` not the app's urls:

```python
path("members/", include("django.contrib.auth.urls")),
```

**Exercise:** Protect one view with `@login_required`, then try opening it while logged out.

---

## C. Working with Django signals and Celery tasks

### Signals

Signals run code automatically when something happens, such as a model being saved.

```python
# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ReadingLog

@receiver(post_save, sender=ReadingLog)
def log_new_reading(sender, instance, created, **kwargs):
    if created:
        print(f"New reading saved: {instance}")
```

Load the signals in `apps.py`:

```python
class MyappConfig(AppConfig):
    name = "myapp"

    def ready(self):
        from . import signals  # noqa
```

### Celery (basic idea - do not run)

Celery runs slow jobs in the background so your page doesn't wait. It needs a message broker such as Redis.

```bash
pip install celery redis
```

```python
# members/tasks.py
from celery import shared_task

@shared_task
def say_hello(name):
    return f"Hello, {name}!"
```

Also create a `celery.py` file:

```python
# book_club/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_club.settings")
app = Celery("book_club")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

And the following:

```python
# book_club/__init__.py
from .celery import app as celery_app
__all__ = ("celery_app",)
```

```python
say_hello.delay("Sam")   # runs in the background
```

**Exercise:** Add the signal above and create a ReadingLog in the admin. Watch for the message in the terminal. (Celery is optional here: it needs Redis and extra setup.)

---

## D. Using Django's caching framework

Caching stores results so Django doesn't have to compute them again.

**Settings (simple in-memory cache):**

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
```

**Cache a whole view for 5 minutes:**

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)
def book_list(request):
    ...
```

**Cache a single value by hand:**

```python
from django.core.cache import cache

count = cache.get("member_count")
if count is None:
    count = Member.objects.count()
    cache.set("member_count", count, 60)   # keep for 60 seconds
```

**Task:** Cache `Member.objects.count()` for 60 seconds, add a member, and see when the number updates.

---

## Quick checklist

- [ ] Custom middleware prints to the terminal
- [ ] A view is protected with `@login_required`
- [ ] A signal fires when a ReadingLog is created
- [ ] A value or view is cached
