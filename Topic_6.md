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

### What is middleware?

Middleware is a layer of code that sits between the web server and your views. Every request passes through it on the way in, and every response passes through it again on the way out.

```
Browser
   │  request                                     ▲  response
   ▼                                              │
┌─────────────────────────────────────────────────────┐
│ Middleware 1  (for example SecurityMiddleware)      │
│  ┌───────────────────────────────────────────────┐  │
│  │ Middleware 2  (for example SessionMiddleware) │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │ Middleware 3 ...                        │  │  │
│  │  │         ┌──────────────┐                │  │  │
│  │  │         │     View     │                │  │  │
│  │  │         └──────────────┘                │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```
Middleware is the right place for work that applies to every request, such as:

- handling logins
- adding security headers
- logging and timing requests
- redirecting or blocking certain requests
- blocking the views during maintenance

You have already been using it. Open book_club/settings.py and find the MIDDLEWARE list. It looks like this:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```
### Anatomy of a middleware

A middleware is a class with two methods:

```python
class ExampleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response      # runs once, when the server starts

    def __call__(self, request):
        # 1. Code here runs BEFORE the view (and before any middleware below it)
        response = self.get_response(request) # pass the request on

        # 2. Code here runs AFTER the view, on the way back out
        return response
```

To illustrate how middleware works, create the following class inside `members/middleware.py`:

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

Middleware runs top to bottom on the way in, and bottom to top on the way out. Add the middleware, run the server, open a page, and watch the terminal output.

### Another Example: timing every request in the members app

We can build a middleware that measures how long each request takes. It prints the time in the terminal and adds a header to the response, which is handy when you are looking for slow pages:

1. Create a new class in `members/middleware.py` called RequestTimingMiddleware.
2. Add the following code to run before the view:
```python
start = time.perf_counter()
```
3. Add the following code to run after the view:
```python
duration_ms = (time.perf_counter() - start) * 1000
response["X-Response-Time-ms"] = f"{duration_ms:.1f}"
print(f"{request.method} {request.path} took {duration_ms:.1f} ms")
```
Register this new middleware. Now rerun the server and check what happens when you navigate the site.

## Exercise: count page views per visitor

Write a third middleware, `PageViewCounterMiddleware`, that counts how many pages each visitor has viewed during their session. Then show the count in the footer of your site.

**Steps**

1. In `members/middleware.py`, add a new class with the same structure as the ones above.
2. Before calling `get_response`, increase a counter stored in the session:

```python
request.session["page_views"] = request.session.get("page_views", 0) + 1
```

3. Register it in `MIDDLEWARE`. **Think about the order:** it uses `request.session`, so it must come **after** `SessionMiddleware`.
4. Show the number in the footer of `members/templates/members/base.html`:

```html
<p>Pages viewed this session: {{ request.session.page_views }}</p>
```

5. Refresh the page several times and watch the number grow.

**Questions to think about**

- What happens if you put your middleware **above** `SessionMiddleware`? Try it and read the error.
- The count also goes up for static files such as the CSS file. How could you skip requests whose path starts with `/static/`? (Hint: `request.path.startswith(...)`.)
- Why is the counter increased *before* `get_response` and not after?

---

## B. Customizing authentication and authorization

Django has a lot of functionality which allows the developer to authorise and authenticate users. Most of this functionality comes from the `django.contrib.auth.middleware.AuthenticationMiddleware` middleware and we don't need to change anything to use it.

For example, we can add a log in to access certain views. For example:

**Require login for a view:**

Requiring log in to access a particular view is extremely easy. All you need is to use a python function decorator to require login, such as:

```python
from django.contrib.auth.decorators import login_required

@login_required
def add_member(request):
    ...
```
For class views, for example when using generic views, include a mixin to get the same behaviour, for example:

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class MemberListView(LoginRequiredMixin,, ListView):
    model = Member
    ...

class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member
    ...
```

To tell Django where users get sent to after logging in and logging out we need to define these locations in the settings file:

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

**Exercise:** Protect at least one view with `@login_required`, and another with both `@login_required` and 
`@permission_required`. Add new users to the admin module and test you site's authentication behaviour with these new users. What happens if a user is a valid user but does not have permission to access a view?

Try creating a better template to display when permission is not granted. You just need to add a new `403.html` template to your application.

---

## C. Working with Django signals and Celery tasks

### Signals

A signal lets one part of your code announce “something just happened,” and lets other code react without the original code knowing about it. Django sends signals for many events, such as a model being saved, deleted, or a user logging in. You write a small function (a receiver) and attach it to a signal. Django calls it every time that event occurs.

For example, when you save a new entry in the ReadingLog table (this can be done from the admin, form, shell or anywhere), Django can fire a signal when it saves the new entry (post_save signal). Your receiver will receive the signal automatically and the code that saves the ReadingLog does not need to be changed.

This particular signal can be done using the following code:

First create a new signal in a `members/signals.py` file with the code below.

```python
# members/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ReadingLog

@receiver(post_save, sender=ReadingLog)
def log_new_reading(sender, instance, created, **kwargs):
    if created:
        print(f"New reading saved: {instance}")
```

The code above is a receiver function that gets the signal from ReadingLog, when this table is saved.

The only extra step that is needed is to load signals from `members/apps.py`. Without loading the signal from apps Django cannot reach the signals functionality. It's a bit of a trick to make signals work.

```python
from django.apps import AppConfig

class MembersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "members"

    def ready(self):
        from . import signals 
```
**Exercise:** To test it, create a new reading log entry and check the terminal. You will see the output of print(f"New reading saved: {instance}").

Instead of printing, a receiver can do useful work, such as sending a welcome email when a Member is created.

### Celery (check basic idea - do not run)

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

In settings:
```python
CELERY_BROKER_URL = "redis://localhost:6379/0"
```

```python
say_hello.delay("Sam" , countdown=60)   # runs in the background
```

To summarise, celery is a task queue that runs slow or scheduled work in the background, outside the request/response cycle, so your views can respond immediately. In the Book Club project, you could use it to send a welcome email when a new member is added (send_welcome_email.delay(member.id)), to email a monthly "books read" summary to every member on a schedule (using Celery Beat), or to generate a large export of reading logs as a CSV without making the visitor wait.

It needs a message broker such as Redis or RabbitMQ and a separate worker process, so we will not run celery tasks in this workshop. For more information check: https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html

---

## D. Using Django's caching framework

Caching stores results so Django doesn't have to compute them again. Some work is slow or repeated: a database query that counts thousands of rows, a page built from many queries, a call to an outside API. Caching saves the result in storage the first time. Later requests read the saved copy instead of repeating the work.

First request  → compute result (slow) → save it in the cache → return it.

Next requests  → found in the cache (fast) → return it.

After timeout  → cache entry expires → next request computes it again (slow).

The tradeoff is that cached data can be stale. If a member is added during the timeout window, a cached count won’t show it until the entry expires or you delete it.

**Settings (simple in-memory cache):**

To operate a caching feature we need to add a cache to the settings file. We can use a small one available from Django just to test how this feature works. Add the following lines to `book_club/settings.py`:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
```

**Cache a whole view for 60 seconds:**

One thing we could cache in our members application is the members list. We don't have many members but assuming the list could be very long, we could potentially cache it for a given amount of time. For example, we could cache the list view for 60 seconds by adding a decorator to the respective view:

```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
...

@method_decorator(cache_page(60), name="dispatch")
class MemberListView(LoginRequiredMixin, ListView):
    model = Member
    ...
```

### Caching a single value

Caching a whole page is not always what you want. Sometimes only one value is slow to compute, such as a count or an average. For this, you store the value yourself and follow a simple pattern:

1. Look in the cache.
2. If the value is there (a **hit**), use it.
3. If not (a **miss**), compute it, store it with an expiry time, and use it.

Create `members/utils.py`:

```python
from django.core.cache import cache

from .models import Member


def get_member_count():
    count = cache.get("member_count")
    if count is None:                                  # cache miss
        count = Member.objects.count()
        cache.set("member_count", count, timeout=60)   # keep it for 60 seconds
    return count
```

Django also offers a shortcut for the same pattern:

```python
cache.get_or_set("member_count", Member.objects.count, timeout=60)
```

#### Try it in the shell

```bash
python manage.py shell
```

```python
from django.core.cache import cache
from members.models import Member
from members.utils import get_member_count

get_member_count()                  # 4   (miss: read from the database and cached)
get_member_count()                  # 4   (hit: no database query)

Member.objects.create(name="Test Person", email="test@example.com")
Member.objects.count()              # 5   (the database is up to date)
get_member_count()                  # 4   (still the cached, now outdated, value)

cache.delete("member_count")        # remove the cached value by hand
get_member_count()                  # 5   (miss again: fresh count)
```

The cached number stays outdated until it **expires** (after 60 seconds) or you **delete** it. This is the main trade-off of caching: faster answers, but possibly stale data.

Clean up the test data:

```python
Member.objects.filter(email="test@example.com").delete()
cache.delete("member_count")
```

> **Do the whole test in one shell session.** `LocMemCache` stores data in the memory of one Python process. The shell and `runserver` are different processes, so each has its own separate cache. A value cached by the shell is invisible to the web server, and the other way round.

**Exercise:** Use the cached count on the home page and watch it go stale.

1. In `members/utils.py`, change the timeout to `10` seconds so the effect is easy to see.
2. In the `home` view, replace `Member.objects.count()` with `get_member_count()`, importing it from `.utils`.
3. Open the home page and note the member count.
4. Add a member at `<site>/members/add/`, then go back to the home page straight away. Does the count change?
5. Wait 10 seconds and reload. When does it update?

**Challenge:** make the count update immediately after a member is added. Override `form_valid` in `MemberCreateView` to delete the cached value (`cache.delete("member_count")`) before saving. Does the count update now when you add a member in the **admin** instead? Why or why not?

---

## Quick checklist

- [ ] Custom middleware prints to the terminal
- [ ] A view is protected with `@login_required` and other views with `@login_required` and `@permission_required`.
- [ ] A signal fires when a ReadingLog is created
- [ ] A value or view is cached
