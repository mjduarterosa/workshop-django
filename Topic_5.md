# V. Forms and User Input (2 hours)

| Section | Topic |
|---|---|
| A | Working with Django forms | 
| B | Validating user input | 
| C | Rendering forms in templates | 
| D | Customizing form behavior and appearance | 

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
            return redirect("member_list")
    else:
        form = MemberForm()
    return render(request, "add_member.html", {"form": form})
```

**Task:** Create `MemberForm`, the `add_member` view, and a URL for it.

---

## B. Validating user input

`is_valid()` checks every field. Add your own rules with `clean_<fieldname>()`:

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

**Task:** Add a `clean_firstname` that rejects names shorter than 2 characters.

---

## C. Rendering forms in templates

```html
<!-- templates/add_member.html -->
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Save</button>
</form>
```

- `{% csrf_token %}` is required for POST forms.
- `{{ form.as_p }}` wraps each field in a `<p>`. Alternatives: `form.as_table`, `form.as_ul`.

Render fields manually for more control:

```html
{% for field in form %}
  <div>
    {{ field.label_tag }} {{ field }}
    {{ field.errors }}
  </div>
{% endfor %}
```

**Task:** Render the form with `as_p`, then switch to the manual loop.

---

## D. Customizing form behavior and appearance

Change widgets, labels, and help text:

```python
class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["firstname", "lastname", "email", "joined_date"]
        labels = {"firstname": "First name"}
        help_texts = {"email": "We will never share your email."}
        widgets = {
            "joined_date": forms.DateInput(attrs={"type": "date"}),
            "firstname": forms.TextInput(attrs={"class": "input", "placeholder": "Jane"}),
        }
```

- `attrs` adds HTML attributes (CSS classes, placeholders).
- To make a field optional or required, set `required=False` or `True` on a regular `forms.Form` field.

**Task:** Give `joined_date` a date picker widget and add a CSS class to one field.

---

## Quick checklist

- [ ] Form class created
- [ ] View handles GET and POST
- [ ] Custom validation works
- [ ] Template shows form and errors
- [ ] Widgets and labels customized
