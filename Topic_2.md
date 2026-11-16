# II. URL Routing and Views (2 hours)

| Section | Topic |
|---|---|
| A | Understanding URL routing in Django |
| B | Creating views to handle HTTP requests |
| C | Working with URL patterns and regular expressions |
| D | Using generic views for common tasks |

In this part we build a small **Book Club** site. The project is called `book_club` and the app is called `members`.

---

## Setup

### 1. Create a simple model

Sections B to D need some data to show, so we create a minimal `Member` model. (Models are covered in more depth later in the course.)

Edit `members/models.py`:

```python
from django.db import models

class Member(models.Model):
  firstname = models.CharField(max_length=255)
  lastname = models.CharField(max_length=255)
```

Create and apply the migrations:

```bash
python manage.py makemigrations members
python manage.py migrate
```

### 2. Add sample data

Open the Django shell:

```bash
python manage.py shell
```

Paste the following, then type `exit()`:

```python
from members.models import Member

member = Member(firstname='Joana', lastname='Silva')
member.save()
```

### 3. Running the server

**Codespaces:** `python manage.py runserver 0.0.0.0:8000`, then open the **Ports** tab and click the globe icon next to port 8000.

**Local:** `python manage.py runserver`, then open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## A. Understanding URL routing in Django

### How a request is handled

```
Browser  →  book_club/urls.py  →  members/urls.py  →  view function  →  response
            (project routes)      (app routes)
```

1. The browser requests a URL, such as `/hello/`.
2. Django checks the patterns in the project's `urls.py`, from top to bottom.
3. When a pattern matches, Django calls the view attached to it, passing any captured values.
4. The view returns a response, which goes back to the browser.

In Topic 1, we have already create a view and called "members" and we have added the corresponding url to the app urls file and then did the routing to the project urls file as well. Let's try to capture now a value from a url.

### Step 1: Write new view and add new URL

In `members/views.py` add:

```python
def home(request):
    return HttpResponse("Welcome to the Book Club!")
```

To `members/urls.py` add:

```python
urlpatterns = [
    path("members/", views.members, name="members"),
    path("", views.home, name="home"),
]
```

### Step 2: Capture a value from the URL

Add to `members/views.py`:

```python
def hello(request, name):
    return HttpResponse(f"Hello, {name}! Welcome to the Book Club.")
```

Add to `urlpatterns` in `members/urls.py`:

```python
    path("hello/<str:name>/", views.hello, name="hello"),
```

The `<str:name>` part captures that piece of the URL and passes it to the view as the argument `name`.

### Step 3: Test it

| Open this URL | You should see |
|---|---|
| `""` | Welcome to the Book Club! |
| `/hello/Joana/` | Hello, Joana! Welcome to the Book Club. |
| `/hello/` | A 404 page (no route matches) |

### Checkpoint

- [ ] `/` shows the welcome message
- [ ] `/hello/<any name>/` greets that name

### Exercise

Add a route `about/` with a view that returns a short description of the club.

---

## B. Creating views to handle HTTP requests

A view is a Python function that takes a `request` and returns a response.

### 1. The request object

Add to `members/views.py`:

```python
def request_info(request):
    name = request.GET.get("name", "stranger")
    text = (
        f"Method: {request.method}\n"
        f"Path: {request.path}\n"
        f"Hello, {name}!"
    )
    return HttpResponse(text, content_type="text/plain")
```

Add to `members/urls.py`:

```python
    path("info/", views.request_info, name="info"),
```

Test it:

| Open this URL | You should see |
|---|---|
| `/info/` | Method: GET, Path: /info/, Hello, stranger! |
| `/info/?name=Alice` | Method: GET, Path: /info/, Hello, Alice! |

Useful attributes: `request.method`, `request.path`, `request.GET` (query string values), `request.POST` (submitted form values), `request.user`.

### 2. Rendering templates

Create the folders and the base template at `members/templates/members/base.html`. The folder name `members` appears twice on purpose. It stops template names clashing between apps.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{% block title %}Home{% endblock %}</title>
</head>
<body>
  <nav>
    <a href="{% url 'members:home' %}">Home</a> |
    <a href="{% url 'members:list' %}">Members</a>
  </nav>
  <hr>
  {% block content %}{% endblock %}
</body>
</html>
```

Create `members/templates/members/member_list.html`:

```html
{% extends "members/base.html" %}

{% block title %}Members{% endblock %}

{% block content %}
  <h1>Book Club Members</h1>
  <ul>
    {% for member in members %}
      <li>
        <a href="{% url 'members:detail' member.id %}">{{ member.firstname }} {{ member.lastname }}</a>
        &mdash; {{ member.joined_date }}
      </li>
    {% empty %}
      <li>No members yet.</li>
    {% endfor %}
  </ul>
{% endblock %}
```

Create `members/templates/members/member_detail.html`:

```html
{% extends "members/base.html" %}

{% block title %}{{ member.id }}{% endblock %}

{% block content %}
  <h1>{{ member.firstname }} {{ member.lastname}}</h1>
  <p>Email: {{ member.email }}</p>
  <p>Phone: {{ member.phone }}</p>
  <p>Joined: {{ member.joined_date }}</p>
  <p><a href="{% url 'members:list' %}">Back to the list</a></p>
{% endblock %}
```

Add the views to `members/views.py`, updating the imports at the top:

```python
from django.shortcuts import get_object_or_404, redirect, render
from .models import Member
```

```python
def member_list(request):
    members = Member.objects.all()
    return render(request, "members/member_list.html", {"members": members})


def member_detail(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    return render(request, "members/member_detail.html", {"member": member})
```

Also update:
```python
def home(request):
    return render(request, "members/home.html")
```

Add the routes:

```python
    path("members/", views.member_list, name="list"),
    path("members/<int:member_id>/", views.member_detail, name="detail"),
```

`get_object_or_404` returns the object, or automatically sends a 404 response if it does not exist.

Before running the server again, the above code only works if the model Member is updated with new fields.

### 3. Add new fields to model
In `members/models.py` add the following code to the Member class:
```python
    email = models.CharField(max_length=255, null=True)
    phone = models.IntegerField(null=True)
    joined_date = models.DateField(null=True)
```
Use the shell to add more data. Now run the server and check the new layout and urls.

### 4. Redirects and errors

Update the imports at the top of `members/views.py`:

```python
from django.http import Http404, HttpResponse, JsonResponse
```

Add a view that redirects to the most recent member:

```python
def latest_member(request):
    member = Member.objects.order_by("-joined").first()
    if member is None:
        raise Http404("No members yet")
    return redirect("members:detail", member_id=member.id)
```

Add the route:

```python
    path("members/latest/", views.latest_member, name="latest"),
```

### 5. Restricting HTTP methods

Add the decorator import at the top of `members/views.py`:

```python
from django.views.decorators.http import require_GET
```

Decorate the JSON view so it only accepts GET requests:

```python
@require_GET
def member_list_json(request):
    members = list(Member.objects.values("id", "name", "favorite_book"))
    return JsonResponse({"members": members})
```

Other methods now receive a `405 Method Not Allowed` response.

### Test it

| Open this URL | You should see |
|---|---|
| `<site>/members/` | A list of four members with links |
| `<site>/members/2/` | Bob Smith's detail page |
| `<site>/members/999/` | A 404 page |
| `<site>/members/latest/` | A redirect to David Lee's detail page |

### Checkpoint

- [ ] The member list shows all members
- [ ] Clicking a member opens the detail page
- [ ] A non-existent ID shows a 404

### Exercise

Add a `favorite_book` line to the list page that shows "Not set" when it is empty. Hint: use the `|default:"Not set"` template filter.

---

## C. Working with URL patterns and regular expressions

### 1. Path converters

| Converter | Matches | Example |
|---|---|---|
| `str` | Any non-empty text without `/` (the default) | `hello/<str:name>/` |
| `int` | Zero or a positive whole number | `members/<int:member_id>/` |
| `slug` | Letters, numbers, hyphens and underscores | `books/<slug:slug>/` |
| `uuid` | A formatted UUID | `orders/<uuid:id>/` |
| `path` | Any text, including `/` | `files/<path:filepath>/` |

A route can capture several values. Add a view to `members/views.py`:

```python
def members_by_year(request, year):
    members = Member.objects.filter(joined__year=year)
    return render(request, "members/member_list.html", {"members": members})
```

Add the route:

```python
    path("members/archive/<int:year>/", views.members_by_year, name="archive"),
```

| Open this URL | You should see |
|---|---|
| `<site>/members/archive/2024/` | Alice and Bob |
| `<site>/members/archive/2025/` | Carla and David |
| `<site>/members/archive/abc/` | A 404 (`int` does not match `abc`) |

### 2. Pattern order matters

Django uses the **first** pattern that matches. Imagine you had written this in `members/urls.py`:

```python
    path("members/<str:anything>/", views.some_view),   # matches /members/json/ too!
    path("members/json/", views.member_list_json),      # never reached
```

Always put the specific routes before the general ones.

### 3. Regular expressions with `re_path`

When converters are not precise enough, use `re_path` with a regular expression. Update the import at the top of `members/urls.py`:

```python
from django.urls import path, re_path
```

Add two views to `members/views.py`:

```python
def members_by_month(request, year, month):
    members = Member.objects.filter(joined__year=int(year), joined__month=int(month))
    return render(request, "members/member_list.html", {"members": members})


def members_by_initial(request, letter):
    members = Member.objects.filter(name__istartswith=letter)
    return render(request, "members/member_list.html", {"members": members})
```

Add the routes:

```python
    re_path(
        r"^members/archive/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$",
        views.members_by_month,
        name="archive-month",
    ),
    re_path(
        r"^members/initial/(?P<letter>[A-Za-z])/$",
        views.members_by_initial,
        name="initial",
    ),
```

| Open this URL | You should see |
|---|---|
| `<site>/members/archive/2024/03/` | Alice and Bob |
| `<site>/members/archive/2025/06/` | David |
| `<site>/members/archive/2025/6/` | A 404 (month must be two digits) |
| `<site>/members/initial/c/` | Carla |
| `<site>/members/initial/cc/` | A 404 (only one letter allowed) |

**How to read the regular expression**

| Part | Meaning |
|---|---|
| `^` and `$` | The route must match from the start to the end |
| `(?P<year>...)` | A **named group**: the captured text is passed to the view as `year` |
| `[0-9]{4}` | Exactly four digits |
| `[A-Za-z]` | One letter, upper or lower case |

Values captured by `re_path` always arrive as **strings**, which is why the view converts them with `int()`.

### 4. Reversing URLs

Never hard-code URLs. Use the route name instead:

```python
from django.urls import reverse

reverse("members:detail", args=[2])          # '/members/2/'
reverse("members:archive", args=[2024])      # '/members/archive/2024/'
reverse("members:initial", args=["c"])       # '/members/initial/c/'
```

In templates, use the `url` tag:

```html
<a href="{% url 'members:archive' 2024 %}">Joined in 2024</a>
```

Try it in the shell with `python manage.py shell`. If you later change a route, every link updates automatically.

### Checkpoint

- [ ] `/members/archive/2024/` and `/members/archive/2024/03/` both work
- [ ] `/members/initial/c/` lists Carla
- [ ] You can explain why `/members/archive/2025/6/` returns a 404

### Exercise

Add a route `members/joined/<int:year>-<int:month>/` using `path` and write the matching view.

---

## D. Using generic views for common tasks

Django ships with **class-based generic views** for common jobs such as listing objects, showing one object, or handling a form. They replace repeated code with a few settings.

### 1. Replace the list and detail views

Update the imports at the top of `members/views.py`:

```python
from django.views.generic import DetailView, ListView
```

Add:

```python
class MemberListView(ListView):
    model = Member
    template_name = "members/member_list.html"
    context_object_name = "members"


class MemberDetailView(DetailView):
    model = Member
    template_name = "members/member_detail.html"
    context_object_name = "member"
```

They reuse the templates from Section B. Update `members/urls.py` by replacing the two function-based routes:

```python
    path("members/", views.MemberListView.as_view(), name="list"),
    path("members/<int:pk>/", views.MemberDetailView.as_view(), name="detail"),
```

The detail route now uses `pk`, which is the name `DetailView` expects by default. The `{% url 'members:detail' member.id %}` links in the templates still work, because they pass the value by position.

You can now delete `member_list` and `member_detail` from `members/views.py`, since nothing uses them. Update `latest_member` to match the new parameter name:

```python
    return redirect("members:detail", pk=member.id)
```

Check `/members/`, `/members/2/` and `/members/latest/`.

### 2. TemplateView for static pages

Add to the import in `members/views.py`:

```python
from django.views.generic import DetailView, ListView, TemplateView
```

```python
class AboutView(TemplateView):
    template_name = "members/about.html"
```

Create `members/templates/members/about.html`:

```html
{% extends "members/base.html" %}

{% block content %}
  <h1>About the Book Club</h1>
  <p>We meet every month to discuss a book chosen by a member.</p>
{% endblock %}
```

Add the route:

```python
    path("about/", views.AboutView.as_view(), name="about"),
```

### 3. RedirectView

Add the import to `members/urls.py`:

```python
from django.views.generic import RedirectView
```

Add a route that sends an old address to the new one:

```python
    path("people/", RedirectView.as_view(pattern_name="members:list"), name="people"),
```

Opening `<site>/people/` now redirects to `/members/`.

### 4. CreateView for forms

Update the imports in `members/views.py`:

```python
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView
```

Add:

```python
class MemberCreateView(CreateView):
    model = Member
    fields = ["name", "email", "favorite_book"]
    template_name = "members/member_form.html"
    success_url = reverse_lazy("members:list")
```

Create `members/templates/members/member_form.html`:

```html
{% extends "members/base.html" %}

{% block content %}
  <h1>Add a member</h1>
  <form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save</button>
  </form>
{% endblock %}
```

Add the route:

```python
    path("members/add/", views.MemberCreateView.as_view(), name="add"),
```

Add a link to the form in `members/templates/members/base.html` by extending the navigation:

```html
    <a href="{% url 'members:list' %}">Members</a> |
    <a href="{% url 'members:add' %}">Add member</a>
```

Open `<site>/members/add/`, submit the form, and the new member appears in the list.

### The complete `members/urls.py`

Here is the file as it should look at the end of this part:

```python
from django.urls import path, re_path
from django.views.generic import RedirectView

from . import views

app_name = "members"

urlpatterns = [
    path("", views.home, name="home"),
    path("hello/<str:name>/", views.hello, name="hello"),
    path("info/", views.request_info, name="info"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("people/", RedirectView.as_view(pattern_name="members:list"), name="people"),
    path("members/", views.MemberListView.as_view(), name="list"),
    path("members/json/", views.member_list_json, name="list-json"),
    path("members/latest/", views.latest_member, name="latest"),
    path("members/add/", views.MemberCreateView.as_view(), name="add"),
    path("members/<int:pk>/", views.MemberDetailView.as_view(), name="detail"),
    path("members/archive/<int:year>/", views.members_by_year, name="archive"),
    re_path(
        r"^members/archive/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$",
        views.members_by_month,
        name="archive-month",
    ),
    re_path(
        r"^members/initial/(?P<letter>[A-Za-z])/$",
        views.members_by_initial,
        name="initial",
    ),
]
```

### Function views or class-based views?

| | Function-based views | Class-based generic views |
|---|---|---|
| Best for | Custom logic that is unique to one page | Standard tasks: list, detail, create, update, delete |
| Code size | More code for standard tasks | Very little code |
| Easy to read | Everything is visible in one place | Need to know what the base class does |

Both are normal Django. Use generic views for standard tasks and function views when you need full control.

### Checkpoint

- [ ] `/members/` and `/members/<id>/` work using generic views
- [ ] `/about/` shows the about page
- [ ] `/people/` redirects to `/members/`
- [ ] `/members/add/` adds a new member that appears in the list

### Exercise

Add an `UpdateView` that lets you edit a member and a `DeleteView` that removes one. Use `fields`, `template_name` and `success_url` as in `MemberCreateView`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `NoReverseMatch` error | The name in `{% url %}` or `reverse()` does not exist. Check `app_name` and the route's `name` |
| `TemplateDoesNotExist` | Check the path is `members/templates/members/<file>.html` and that `"members"` is in `INSTALLED_APPS` |
| `no such table: members_member` | Run `python manage.py makemigrations members` and then `python manage.py migrate` |
| `got an unexpected keyword argument 'member_id'` | The view's argument name must match the name in the route. Generic views expect `pk` |
| 404 on a route you just added | Check the route is in `members/urls.py` and appears before any general pattern |
| `DisallowedHost` (Codespaces) | Add the settings block from Setup step 2 and restart the server |
| `CSRF verification failed` on a form (Codespaces) | The `CSRF_TRUSTED_ORIGINS` block is missing, or the template has no `{% csrf_token %}` |