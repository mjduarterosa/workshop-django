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

**Task:** Add the middleware, run the server, open a page, and watch the terminal output.

---

## B. Customizing authentication and authorization

**Require login for a view:**

```python
from django.contrib.auth.decorators import login_required

@login_required
def member_list(request):
    ...
```

Set where users get sent to log in:

```python
# settings.py
LOGIN_URL = "/accounts/login/"
```

**Require a permission:**

```python
from django.contrib.auth.decorators import permission_required

@permission_required("myapp.add_member", raise_exception=True)
def add_member(request):
    ...
```

**Check in a template:**

```html
{% if user.is_authenticated %}
  Hello, {{ user.username }}
{% else %}
  <a href="{% url 'login' %}">Log in</a>
{% endif %}
```

**Task:** Protect one view with `@login_required`, then try opening it while logged out.

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

### Celery (basic idea)

Celery runs slow jobs in the background so your page doesn't wait. It needs a message broker such as Redis.

```bash
pip install celery redis
```

```python
# myapp/tasks.py
from celery import shared_task

@shared_task
def say_hello(name):
    return f"Hello, {name}!"
```

```python
say_hello.delay("Sam")   # runs in the background
```

**Task:** Add the signal above and create a ReadingLog in the admin. Watch for the message in the terminal. (Celery is optional here: it needs Redis and extra setup.)

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
