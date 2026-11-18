# IV. Models and Databases (2 hours)

| Section | Topic |
|---|---|
| A | Introduction to Django's models and ORM | 
| B | Defining models and fields | 
| C | Using the Django shell for database interactions | 
| D | Migrating and updating the database schema | 
| E | Managing data with the Django admin | 

This part continues the **Book Club** project (project `book_club`, app `members`). We already have a `Member` model. Now we add models for **books** and for **which member has read which book**, then learn to manage all of it from Django's built-in admin site.

All file paths below are relative to the folder that contains `manage.py`.

---

## A. Introduction to Django's models and ORM

See slides.

### Where the data lives

Look at `DATABASES` in `book_club/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

SQLite stores everything in the single file `db.sqlite3` next to `manage.py`. It needs no setup, which makes it ideal for learning.

**Try it:** in Codespaces, click `db.sqlite3` in the VS Code file explorer. The SQLite Viewer extension (installed by our devcontainer) shows every table and its rows. Locally, install the "SQLite Viewer" extension in VS Code to do the same. Find the `members_member` table and look at its columns.

---

## B. Defining models and fields

### 1. The new models

We add two models:

- **`Book`**: a book the club knows about (title, author, and so on).
- **`ReadingLog`**: a record that says "this member has read this book", with the date finished.

Two members can read the same book, and one member reads many books. `ReadingLog` connects the two: it holds a **foreign key** (a link) to a `Member` and to a `Book`.

```
Member  1 ───── many  ReadingLog  many ───── 1  Book
```

### 2. Write the code

Add the following classes to `members/models.py`:

```python
from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    pages = models.PositiveIntegerField(null=True, blank=True)
    published_year = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["title"]
        constraints = [
            models.UniqueConstraint(
                fields=["title", "author"], name="unique_book_title_author"
            )
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"


class ReadingLog(models.Model):
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="readings"
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="readings"
    )
    date_finished = models.DateField(default=date.today)

    class Meta:
        ordering = ["-date_finished"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "book"], name="unique_member_book"
            )
        ]

    def __str__(self):
        return f"{self.member} read {self.book}"
```

### Exercise

Add a `def __str__(self):` to the Member class for a better display of information.

### 3. What each part means

**Common field types**

| Field | Stores | Example in our models |
|---|---|---|
| `CharField(max_length=...)` | Short text | `title`, `author` |
| `PositiveIntegerField` | A whole number that is 0 or more | `pages` |
| `PositiveSmallIntegerField` | A small whole number that is 0 or more | `published_year` |
| `DateField` | A date | `joined`, `date_finished` |
| `ForeignKey` | A link to a row in another table | `member`, `book` |

**Common field options**

| Option | Meaning |
|---|---|
| `max_length` | Maximum number of characters (required for `CharField`) |
| `null=True` | The database column may be empty (`NULL`) |
| `blank=True` | Forms and the admin may leave the field empty |
| `default=...` | The value used when none is given |
| `unique=True` | No two rows may have the same value |
| `choices=...` | Only the listed values are allowed (shown as a dropdown) |
| `validators=[...]` | Extra checks, such as a minimum and a maximum |

`null` is about the database and `blank` is about form validation. For number and date fields you usually need both (`null=True, blank=True`). For text fields, use `blank=True` only, and leave an empty string for "no value".

**Other parts**

| Part | Meaning |
|---|---|
| `ForeignKey(Member, on_delete=models.CASCADE)` | Links each log to one member. `CASCADE` means that deleting a member also deletes their logs |
| `related_name="readings"` | Lets you go backwards: `member.readings.all()` gives all logs for a member |
| `class Meta: ordering` | The default order of results |
| `UniqueConstraint` | A rule enforced by the database. A book title and author pair must be unique, and a member can log a given book only once |
| `__str__` | The text shown for an object in the shell and in the admin |

Other `on_delete` choices include `PROTECT` (refuse to delete while linked rows exist) and `SET_NULL` (clear the link, which needs `null=True`).

### 4. Create the tables

Saving the model file does not change the database yet. Two commands do that:

```bash
python manage.py makemigrations members -n books_and_readings
python manage.py migrate
```

- `makemigrations` compares your models with the existing migrations and writes a new migration file, `members/migrations/0002_books_and_readings.py`.
- `migrate` runs the migration and creates the tables.

Refresh the SQLite Viewer. You should now see `members_book` and `members_readinglog`. We look at migrations in more detail in Section D.

### Checkpoint

- [ ] `migrate` finishes without errors
- [ ] The database has the tables `members_book` and `members_readinglog`
- [ ] You can explain what `ForeignKey` and `on_delete=CASCADE` mean

## C. Using the Django shell for database interactions

The Django shell is a Python prompt with your project loaded. It is the quickest way to try the ORM.

```bash
python manage.py shell
```

Type `exit()` to leave. The prompt shows `>>>`. When you paste a `for` loop, press **Enter twice** at the end to run it.

### 1. Create objects

```python
from datetime import date
from members.models import Book, Member, ReadingLog
```

Create a book in two steps (build it, then save it):

```python
pride = Book(title="Pride and Prejudice", author="Jane Austen", pages=432, published_year=1813)
pride.id          # None: not in the database yet
pride.save()
pride.id          # 1: now it has a primary key
pride             # <Book: Pride and Prejudice by Jane Austen>
```

Or create and save in one call:

```python
Book.objects.create(title="Dune", author="Frank Herbert", pages=412, published_year=1965)
```

Add the rest of the books with a loop (these are sample values):

```python
books = [
    ("Beloved", "Toni Morrison", 324, 1987),
    ("The Hobbit", "J.R.R. Tolkien", 310, 1937),
    ("Gone Girl", "Gillian Flynn", 422, 2012),
]
for title, author, pages, year in books:
    Book.objects.create(title=title, author=author, pages=pages, published_year=year)
```

Now record who read what. Pass **objects**, not ids, to a foreign key:

```python
maria = Member.objects.get(email="mariarosa@email.com")
ReadingLog.objects.create(member=maria, book=pride, date_finished=date(2026, 4, 10))
```

Add more members for example:
```python
ana = Member.objects.create(firstname='Ana', lastname='Santos', email= 'anasantos@email.com', phone=915769899, joined_date= date(2023, 2, 7))
```
And new reading logs:
```python
logs = [
    ("mariarosa@email.com", "Gone Girl", date(2025, 7, 2)),
    ("anasantos@email.com", "Beloved", date(2025, 2, 15)),
]
for member_email, title, finished in logs:
    ReadingLog.objects.create(member=Member.objects.get(email=member_email), book=Book.objects.get(title=title), date_finished=finished)
```

If you run these blocks twice, the unique constraints stop you with an `IntegrityError`. That means the rules are working.

### 2. Read (query) objects

```python
Book.objects.all()                       # every book, ordered by title
Book.objects.count()                     # 5
Book.objects.first()                     # <Book: Beloved by Toni Morrison>
Book.objects.get(title="Dune")           # exactly one match (or an error)
Book.objects.order_by("-published_year").first() # the newest book (Gone Girl)
Book.objects.filter(pages__gt=400)       # more than 400 pages
Book.objects.filter(title__icontains="the")      # case-insensitive "contains"
Book.objects.filter(published_year__lt=1950).count()   # 2
Book.objects.filter(title="Nope").exists()       # False
Book.objects.values("title", "author")   # dictionaries instead of objects
```

`filter()` returns a **QuerySet**, a list-like collection that you can chain: `Book.objects.filter(pages__gt=300).order_by("title")[:3]`.

**Lookups** are the part after the double underscore:

| Lookup | Meaning | Example |
|---|---|---|
| `exact` (default) | Equal to | `title="Dune"` |
| `iexact` | Equal, ignoring case | `title__iexact="dune"` |
| `contains`, `icontains` | Contains text | `title__icontains="the"` |
| `startswith`, `istartswith` | Starts with | `name__istartswith="a"` |
| `gt`, `gte`, `lt`, `lte` | Greater or less than | `pages__gte=400` |
| `year`, `month` | Part of a date | `joined__year=2024` |
| `isnull` | Is empty | `pages__isnull=True` |

`get()` raises an error unless exactly one row matches:

```python
Book.objects.get(title="Nope")
# members.models.Book.DoesNotExist: Book matching query does not exist.
```

### 3. Follow relationships

```python
log = ReadingLog.objects.first()   # the most recent log (ordering is -date_finished)
log.member                         # <Member: Member object (4)>
log.book                           # <Book: Pride and Prejudice by Jane Austen>
```

Going **backwards** uses the `related_name` we chose:

```python
maria.readings.all()               # maria's logs
maria.readings.count()             # 3
dune = Book.objects.get(title="Dune")
dune.readings.all()                # logs for Dune
```

Filtering **across** a relationship uses double underscores:

```python
ReadingLog.objects.filter(member__firstname="Maria")
Book.objects.filter(readings__member=maria)          # the books Maria has read

```

### 4. Update and delete

```python
dune.pages = 500
dune.save()                                          # update one object

temp = Book.objects.create(title="Temporary", author="Nobody")
temp.delete()                                        # delete book
```

Put `dune.pages` back to 412 afterwards.

### 5. Constraints and validators

The database rules are enforced when you save:

```python
ReadingLog.objects.create(member=maria, book=dune)
# django.db.utils.IntegrityError: UNIQUE constraint failed: ...
```

### Exercise

In the shell, find (1) all books with fewer than 250 pages.

---

## D. Migrating and updating the database schema

### 1. What migrations are (optional step)

A **migration** is a Python file that describes one step in the history of your database. Django keeps them in `members/migrations/`, and it records which have been applied in a table called `django_migrations`.

```bash
python manage.py showmigrations members
```

```
members
 [X] 0001_initial
 [X] ...
 [X] 0003_books_and_readings
```

The workflow is always the same:

1. Change `models.py`.
2. `python manage.py makemigrations members`: write the migration file.
3. `python manage.py migrate`: apply it to the database.

### 2. What if a new field has no default? (optional step)

Existing rows need a value for the new column. If you add a required field with no default, for example `rating_note = models.CharField(max_length=50)`, `makemigrations` stops and asks:

```
It is impossible to add a non-nullable field 'rating_note' to readinglog without specifying a default.
 1) Provide a one-off default now
 2) Quit and manually define a default value in models.py
```

Choose **2**, then add `default=""`, `blank=True` or `null=True` to the field. (We did not add `rating_note`, so you do not need to try this.)

### 3. Going back (do not run)

You can undo the latest migration by migrating to the one before it:

```bash
python manage.py migrate members 0002
python manage.py showmigrations members      # 0003 is now unchecked
python manage.py migrate                     # apply it again
```

Rolling back removes the columns that the migration added, along with their data.

### 8. Rules to remember

- **Commit migration files to Git.** They are the history of your schema, and everyone else needs them.
- **Do not commit `db.sqlite3`.** It is ignored in our `.gitignore`. Each person has their own database, and teammates run `migrate` to build theirs.
- **Never edit a migration that has already been applied or shared.** Make a new one instead.
- If you are stuck in development and do not mind losing your data, you can delete `db.sqlite3` and run `migrate` again. You will need to recreate the sample data, and your superuser from Section E.


### Exercise

Add a `cover_url = models.URLField(blank=True)` field to `Book`, then create and apply the migration. Look at the new migration file before you apply it.

---

## E. Managing data with the Django admin

Django includes a ready-made website for managing your data. It is generated from your models, so you get forms, search and validation without writing any HTML.

### 1. Create an administrator

```bash
python manage.py createsuperuser
```

Enter a username (e.g. "admin"), an email (optional) and a password. The password is hidden while you type. If Django warns that the password is too simple, you can type `y` to keep it for this workshop. Do not do this on a real site.

### 2. Log in

Make sure the server is running and open `<site>/admin/` (the route comes from `book_club/urls.py`). Log in with your new account.

> **Codespaces:** if the login fails with "CSRF verification failed", check the `CSRF_TRUSTED_ORIGINS` block from the setup in Part II.

You will see **Authentication and Authorization** (users and groups), but not our models yet. Django only shows models you register.

### 3. Register your models

Replace the contents of `members/admin.py`:

```python
from django.contrib import admin

from .models import Book, Member, ReadingLog

admin.site.register(Member)
admin.site.register(Book)
admin.site.register(ReadingLog)
```

Refresh the admin page. A **Members** section appears with **Books**, **Members** and **Reading logs**. Click around. Notice that the readable text comes from each model's `__str__` method.

### 4. Customize how each model looks

The plain registration works, but a `ModelAdmin` class gives you control. Replace `members/admin.py` with:

```python
from django.contrib import admin
from .models import Member, Book, ReadingLog


class ReadingLogInline(admin.TabularInline):
    model = ReadingLog
    extra = 1
    autocomplete_fields = ["book"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "pages", "published_year")
    search_fields = ("title", "author")


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "email", "joined_date", "books_read")
    search_fields = ("firstname", "lastname", "email", "phone")
    list_filter = ("joined_date",)
    date_hierarchy = "joined_date"
    inlines = [ReadingLogInline]

    @admin.display(description="Books read")
    def books_read(self, obj):
        return obj.readings.count()


@admin.register(ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = ("member", "book", "date_finished")
    list_filter = ("date_finished",)
    search_fields = ("member__firstname", "member__lastname", "book__title")
    autocomplete_fields = ("member", "book")
    date_hierarchy = "date_finished"
```

The server reloads automatically. Refresh the admin.

**What each setting does**

| Setting | Effect |
|---|---|
| `list_display` | The columns in the list page. It can include methods, like `books_read` |
| `search_fields` | Adds a search box. `member__firstname` searches across a relationship |
| `list_filter` | Adds a filter sidebar |
| `date_hierarchy` | Adds date drill-down links at the top of the list |
| `list_editable` | Lets you edit fields directly in the list and save them all at once |
| `ordering` | The default sort order |
| `fieldsets` | Groups the fields on the edit form. `collapse` hides a group until clicked |
| `inlines` | Shows related rows on the same page, so you can add a member's reading logs on the member page |
| `autocomplete_fields` | Replaces a long dropdown with a search-as-you-type box |
| `@admin.display` | Gives a method a readable column title |

### 5. Manipulate data from the admin

Work through these tasks. Each one shows a different part of the admin:

| Task | How |
|---|---|---|
| **Add** a book | Books → **Add book** → fill in the form → **Save** | 
| **Edit** a book | Click a title in the list, change `pages`, **Save** | 
| **Search** | In Books, type `tolkien` | 
| **Sort** | Click a column heading | 
| **Add a log** | Reading logs → **Add reading log**; pick a member and a book | 
| **Unique constraint** | Add a second log for the same member and book | 
| **Inline editing** | Open a member and use the **Reading logs** table at the bottom to add a log | 
| **Delete** | Add a test member with a reading log, then delete the member | 

Everything you did in the admin could be done in the shell. The admin and the shell use the same ORM and the same database.

### 6. Where the admin fits

The admin is built for the **site owner**, not for the public. It is quick for managing data, adding test content and fixing mistakes. For pages your members use, you write your own views and templates, as in the earlier parts.

### Checkpoint

- [ ] You can log in to `/admin/` and see Books, Members and Reading logs
- [ ] You added a book and a reading log from the admin
