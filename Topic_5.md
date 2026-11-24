# V. Forms and User Input (2 hours)

| Section | Topic |
|---|---|
| A | Working with Django forms | 
| B | Validating user input | 
| C | Rendering forms in templates | 
| D | Customizing form behaviour and appearance | 

Examples use the `Member` model from your project. Create `forms.py` in your app folder.

---

## A. Working with Django forms

Django has two kinds of forms:

- **`forms.Form`**: you define each field yourself.
- **`forms.ModelForm`**: fields are built from a model (less code).

```python
# forms.py
from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["firstname", "lastname", "email", "joined_date"]
```

Handle the form in a view:

```python
# views.py
from django.shortcuts import render, redirect
from .forms import MemberForm

def add_member(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("members:list")
    else:
        form = MemberForm()
    return render(request, "members/add_member.html", {"form": form})
```

Now add the URL for the form:

```python
path("members/add/", views.add_member, name="add_member")
```
---

## B. Validating user input

One important thing when using forms is to make sure the input from the user is validated. Django makes this validation very straightforward. Notice how in the view definition we have `is_valid()` that checks every field in the form. 

You can also add your own rules by defining `clean_<fieldname>()` methods inside your form class:

```python
class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["firstname", "lastname", "email", "joined_date"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not email.endswith("@example.com"):
            raise forms.ValidationError("Use your @example.com address.")
        return email
```

- Use `self.cleaned_data` to read validated values.
- Errors are stored in `form.errors` and shown in the template.

**Exercise:** Add a `clean_phone` that rejects phones that do not start with 9 and do not contain 9 digits.

---

## C. Rendering forms in templates

Create new html template for the form. Notice the code `{% csrf_token %}`. This bit of code is a template tag that adds a hidden security field to a form. It protects your site against CSRF (Cross-Site Request Forgery) attacks. Imagine you're logged in to the Book Club site. You then visit a malicious website that contains a hidden form pointing at your site. Your browser automatically sends your sessionid cookie with that request, so your site would think you submitted it.

When Django renders your form, `{% csrf_token %}` inserts a hidden field with a random secret value. When the form is submitted, the token is sent along with the other fields. `CsrfViewMiddleware` (in your MIDDLEWARE list) compares it with a matching value stored in a cookie and rejects the request if they don't match.

A malicious site can make your browser send the cookie, but it can't read the token, so it can't include the correct one in its forged form. 

```html
{% extends "members/base.html" %}

{% block title %}New member{% endblock %}

{% block content %}
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Save</button>
</form>
{% endblock %}
```

- `{% csrf_token %}` is required for POST forms.
- `{{ form.as_p }}` wraps each field in a `<p>`.

**Exercise:**: Experiment wrapping the form as a table or url to see the difference, using `form.as_table` and `form.as_ul`.

If you would like you can also render the fields manually for more control, for example:

```html
{% for field in form %}
  <div>
    {{ field.label_tag }} {{ field }}
    {{ field.errors }}
  </div>
{% endfor %}
```

**Exercise:** Try the manual loop and change the way the form is shown by default.

---

## D. Customizing form behaviour and appearance

You can also change widgets, labels, and help text in the form to help users of the site knowing what they need to do to complete the form. The following code provides some examples:

```python
class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["firstname", "lastname", "email", "joined_date"]
        labels = {"firstname": "First name"}
        help_texts = {"email": "We will never share your email."}
        widgets = {
            "firstname": forms.TextInput(attrs={"class": "input", "placeholder": "Jane"}),
        }
```

- To make a field optional or required, set `required=False` or `True` on a regular `forms.Form` field.

**Exercise:** Give `joined_date` a date picker widget and add a CSS class to one field.

---
Finally, replace the link on the `members/home.html` page to see all members by the link to add a new member:

```html
<p><a href="{% url 'members:add_member' %}">Add new member</a></p>
```

## Quick checklist

- [ ] Form class created
- [ ] View handles GET and POST
- [ ] Custom validation works
- [ ] Template shows form and errors
- [ ] Widgets and labels customized
