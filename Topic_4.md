# Models and Databases (2 hours)

| Section | Topic | Suggested time |
|---|---|---|
| A | Introduction to Django's models and ORM | 15 min |
| B | Defining models and fields | 25 min |
| C | Using the Django shell for database interactions | 30 min |
| D | Migrating and updating the database schema | 20 min |
| E | Managing data with the Django admin | 30 min |

This part continues the **Book Club** project (project `book_club`, app `members`). We already have a `Member` model. Now we add models for **books** and for **which member has read which book**, then learn to manage all of it from Django's built-in admin site.

All file paths below are relative to the folder that contains `manage.py`.

---

## Setup

You need the project from the earlier parts, with the `members` app, the `Member` model, and the four sample members (Alice Johnson, Bob Smith, Carla Gomez and David Lee).

Check the current state of the database:

```bash
python manage.py showmigrations members
```

You should see `[X] 0001_initial`, which means the `Member` table already exists.

Start the server when you need it:

- **Codespaces:** `python manage.py runserver 0.0.0.0:8000`, then open port 8000 from the **Ports** tab.
- **Local:** `python manage.py runserver`, then open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

In this document, `<site>` means the base address of your running site.

---

## A. Introduction to Django's models and ORM

### Models are Python classes that become database tables

A **model** describes the data your site stores. Django turns each model into a database table, and the **ORM** (Object-Relational Mapper) lets you work with that table using Python instead of SQL.

| Python (the model) | Database |
|---|---|
| A model class (`Member`) | A table (`members_member`) |
| A field (`name = CharField(...)`) | A column |
| An instance (`Member(name="Alice")`) | A row |
| `Member.objects` | The tool for querying the table |

The table name is the app name plus the model name in lower case: `members_member`, and soon `members_book` and `members_readinglog`.

### The same query in SQL and in the ORM

```sql
SELECT * FROM members_member WHERE name LIKE 'A%';
```

```python
Member.objects.filter(name__startswith="A")
```

The ORM gives you three benefits:

- You write Python, not SQL, so one language covers the whole project.
- It protects you from SQL injection, because values are always passed safely.
- It works with several databases (SQLite, PostgreSQL, MySQL). You change one setting, not your code.

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

### Checkpoint

- [ ] You can explain how a model, a field and an instance map to a table, a column and a row
- [ ] You have found `members_member` in the database file

---

## B. Defining models and fields

### 1. The new models

We add two models:

- **`Book`**: a book the club knows about (title, author, genre, and so on).
- **`ReadingLog`**: a record that says "this member has read this book", with the date finished, a rating and notes.

Two members can read the same book, and one member reads many books. `ReadingLog` connects the two: it holds a **foreign key** (a link) to a `Member` and to a `Book`.

```
Member  1 ───── many  ReadingLog  many ───── 1  Book
```

### 2. Write the code

Replace the contents of `members/models.py`. The `Member` model stays exactly as it was:

```python
from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    favorite_book = models.CharField(max_length=200, blank=True)
    joined = models.DateField(default=date.today)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    class Genre(models.TextChoices):
        FICTION = "FIC", "Fiction"
        NONFICTION = "NON", "Non-fiction"
        FANTASY = "FAN", "Fantasy"
        SCIFI = "SCI", "Science fiction"
        MYSTERY = "MYS", "Mystery"
        OTHER = "OTH", "Other"

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    genre = models.CharField(max_length=3, choices=Genre.choices, default=Genre.FICTION)
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
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    notes = models.TextField(blank=True)

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

### 3. What each part means

**Common field types**

| Field | Stores | Example in our models |
|---|---|---|
| `CharField(max_length=...)` | Short text | `title`, `author` |
| `TextField` | Long text | `notes` |
| `EmailField` | Text checked as an email address | `email` |
| `PositiveIntegerField` | A whole number that is 0 or more | `pages` |
| `PositiveSmallIntegerField` | A small whole number that is 0 or more | `rating`, `published_year` |
| `DateField` | A date | `joined`, `date_finished` |
| `BooleanField` | True or False | Added in Section D |
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
| `class Genre(models.TextChoices)` | A tidy way to define `choices`. The first value (`"FIC"`) is stored in the database, and the second (`"Fiction"`) is shown to people |
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

You will see:

```
Migrations for 'members':
  members/migrations/0002_books_and_readings.py
    + Create model Book
    + Create model ReadingLog
    + Create constraint unique_book_title_author on model book
    + Create constraint unique_member_book on model readinglog
```

Refresh the SQLite Viewer. You should now see `members_book` and `members_readinglog`. We look at migrations in more detail in Section D.

### Checkpoint

- [ ] `migrate` finishes without errors
- [ ] The database has the tables `members_book` and `members_readinglog`
- [ ] You can explain what `ForeignKey` and `on_delete=CASCADE` mean

### Exercise

Add a `summary = models.TextField(blank=True)` field to `Book` in your head, and decide which two commands you would run to update the database. (You do the real thing for a different field in Section D.)

---

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
pride = Book(title="Pride and Prejudice", author="Jane Austen", genre=Book.Genre.FICTION, pages=432, published_year=1813)
pride.id          # None: not in the database yet
pride.save()
pride.id          # 1: now it has a primary key
pride             # <Book: Pride and Prejudice by Jane Austen>
```

Or create and save in one call:

```python
Book.objects.create(title="Dune", author="Frank Herbert", genre=Book.Genre.SCIFI, pages=412, published_year=1965)
```

Add the rest of the books with a loop (these are sample values):

```python
books = [
    ("Beloved", "Toni Morrison", Book.Genre.FICTION, 324, 1987),
    ("The Hobbit", "J.R.R. Tolkien", Book.Genre.FANTASY, 310, 1937),
    ("Gone Girl", "Gillian Flynn", Book.Genre.MYSTERY, 422, 2012),
    ("Sapiens", "Yuval Noah Harari", Book.Genre.NONFICTION, 443, 2011),
]
for title, author, genre, pages, year in books:
    Book.objects.create(title=title, author=author, genre=genre, pages=pages, published_year=year)
```

Now record who read what. Pass **objects**, not ids, to a foreign key:

```python
alice = Member.objects.get(name="Alice Johnson")
ReadingLog.objects.create(member=alice, book=pride, date_finished=date(2024, 4, 10), rating=5)
```

Add the remaining logs:

```python
logs = [
    ("Alice Johnson", "Dune", date(2024, 7, 2), 4),
    ("Alice Johnson", "Sapiens", date(2025, 2, 15), 4),
    ("Bob Smith", "Dune", date(2024, 5, 20), 5),
    ("Bob Smith", "The Hobbit", date(2024, 9, 8), 4),
    ("Carla Gomez", "Beloved", date(2025, 3, 3), 5),
    ("Carla Gomez", "Pride and Prejudice", date(2025, 4, 12), 3),
    ("David Lee", "The Hobbit", date(2025, 7, 19), 5),
    ("David Lee", "Gone Girl", date(2025, 8, 30), 3),
]
for member_name, title, finished, rating in logs:
    ReadingLog.objects.create(member=Member.objects.get(name=member_name), book=Book.objects.get(title=title), date_finished=finished, rating=rating)
```

If you run these blocks twice, the unique constraints stop you with an `IntegrityError`. That means the rules are working.

### 2. Read (query) objects

```python
Book.objects.all()                       # every book, ordered by title
Book.objects.count()                     # 6
Book.objects.first()                     # <Book: Beloved by Toni Morrison>
Book.objects.get(title="Dune")           # exactly one match (or an error)
Book.objects.filter(genre=Book.Genre.FICTION)    # Beloved and Pride and Prejudice
Book.objects.exclude(genre=Book.Genre.FICTION)   # everything else
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
| `in` | In a list | `genre__in=["FIC", "FAN"]` |
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
log.member                         # <Member: David Lee>
log.book                           # <Book: Gone Girl by Gillian Flynn>
log                                # <ReadingLog: David Lee read Gone Girl by Gillian Flynn>
```

Going **backwards** uses the `related_name` we chose:

```python
alice.readings.all()               # Alice's three logs
alice.readings.count()             # 3
dune = Book.objects.get(title="Dune")
dune.readings.all()                # the two logs for Dune
```

Filtering **across** a relationship uses double underscores:

```python
ReadingLog.objects.filter(member__name="Alice Johnson")
Book.objects.filter(readings__member=alice)          # the books Alice has read
ReadingLog.objects.filter(rating__gte=5)             # all five-star logs
ReadingLog.objects.filter(book__genre=Book.Genre.FANTASY)
```

### 4. Calculate with aggregates

```python
from django.db.models import Avg, Count

ReadingLog.objects.aggregate(Avg("rating"))
# {'rating__avg': 4.22...}

Book.objects.annotate(avg_rating=Avg("readings__rating")).order_by("-avg_rating").first()
# <Book: Beloved by Toni Morrison>   (average rating 5.0)

Member.objects.annotate(books_read=Count("readings")).order_by("-books_read").first()
# <Member: Alice Johnson>            (3 books)
```

`aggregate()` returns one summary value for the whole queryset. `annotate()` adds a calculated value to **each** object.

### 5. Update and delete

```python
dune.pages = 500
dune.save()                                          # update one object

ReadingLog.objects.filter(rating__lt=4).update(notes="Not my favourite")   # update many rows at once

temp = Book.objects.create(title="Temporary", author="Nobody")
temp.delete()                                        # (1, {'members.Book': 1})
```

Put `dune.pages` back to 412 afterwards.

### 6. See the SQL Django writes

```python
print(Book.objects.filter(pages__gt=400).query)
```

You will see a `SELECT ... FROM "members_book" WHERE "members_book"."pages" > 400 ORDER BY ...` statement. The ORM is only building SQL for you.

### 7. Constraints and validators

The database rules are enforced when you save:

```python
ReadingLog.objects.create(member=alice, book=pride, rating=5)
# django.db.utils.IntegrityError: UNIQUE constraint failed: ...
```

Validators are **not** run by `save()`. They run in forms and in the admin, or when you call `full_clean()` yourself:

```python
bad = ReadingLog(member=alice, book=Book.objects.get(title="Beloved"), rating=10)
bad.full_clean()
# django.core.exceptions.ValidationError: {'rating': ['Ensure this value is less than or equal to 5.']}
```

Do not call `bad.save()`. It would store the invalid rating, which shows why validation matters.

### Checkpoint

- [ ] You created 6 books and 9 reading logs
- [ ] `alice.readings.count()` gives `3`
- [ ] You can explain the difference between `filter()` and `get()`
- [ ] You can explain what `alice.readings.all()` does

### Exercise

In the shell, find (1) all books with fewer than 350 pages, (2) all the books Bob has read, and (3) the average rating of `Dune`.

---

## D. Migrating and updating the database schema

### 1. What migrations are

A **migration** is a Python file that describes one step in the history of your database. Django keeps them in `members/migrations/`, and it records which have been applied in a table called `django_migrations`.

```bash
python manage.py showmigrations members
```

```
members
 [X] 0001_initial
 [X] 0002_books_and_readings
```

The workflow is always the same:

1. Change `models.py`.
2. `python manage.py makemigrations members`: write the migration file.
3. `python manage.py migrate`: apply it to the database.

### 2. Add two fields

Edit `members/models.py`. Add an `isbn` field to `Book`, below `published_year`:

```python
    isbn = models.CharField(max_length=13, blank=True)
```

Add a `would_recommend` field to `ReadingLog`, below `notes`:

```python
    would_recommend = models.BooleanField(default=False)
```

### 3. Create and inspect the migration

```bash
python manage.py makemigrations members -n isbn_and_recommend
```

```
Migrations for 'members':
  members/migrations/0003_isbn_and_recommend.py
    + Add field isbn to book
    + Add field would_recommend to readinglog
```

Open `members/migrations/0003_isbn_and_recommend.py`. It is plain Python:

```python
class Migration(migrations.Migration):

    dependencies = [
        ("members", "0002_books_and_readings"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="isbn",
            field=models.CharField(blank=True, max_length=13),
        ),
        migrations.AddField(
            model_name="readinglog",
            name="would_recommend",
            field=models.BooleanField(default=False),
        ),
    ]
```

`dependencies` makes sure migrations run in order. To see the SQL a migration will run, without running it:

```bash
python manage.py sqlmigrate members 0003
```

### 4. Apply it

```bash
python manage.py migrate
```

```
Applying members.0003_isbn_and_recommend... OK
```

Check in the shell that your existing data survived, and the new columns have their default values:

```python
from members.models import Book, ReadingLog
Book.objects.first().isbn                      # ''
ReadingLog.objects.first().would_recommend     # False
```

### 5. What if a new field has no default?

Existing rows need a value for the new column. If you add a required field with no default, for example `rating_note = models.CharField(max_length=50)`, `makemigrations` stops and asks:

```
It is impossible to add a non-nullable field 'rating_note' to readinglog without specifying a default.
 1) Provide a one-off default now
 2) Quit and manually define a default value in models.py
```

Choose **2**, then add `default=""`, `blank=True` or `null=True` to the field. (We did not add `rating_note`, so you do not need to try this.)

### 6. Common changes and what Django does

| Change in `models.py` | What `makemigrations` does |
|---|---|
| Add a field | Creates an `AddField` (needs a default, `blank=True` for text, or `null=True`) |
| Remove a field | Creates a `RemoveField`. **The data in that column is lost** |
| Change a field's options | Creates an `AlterField` |
| Rename a field | Asks "Did you rename...?" Answer `y` to keep the data |
| Add or remove a model | Creates or deletes a table |

### 7. Going back

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

### Checkpoint

- [ ] `showmigrations` shows `0001`, `0002` and `0003`, all applied
- [ ] Open `db.sqlite3` in the viewer: `members_book` now has an `isbn` column
- [ ] You can explain the difference between `makemigrations` and `migrate`

### Exercise

Add a `cover_url = models.URLField(blank=True)` field to `Book`, then create and apply the migration. Look at the new migration file before you apply it.

---

## E. Managing data with the Django admin

Django includes a ready-made website for managing your data. It is generated from your models, so you get forms, search and validation without writing any HTML.

### 1. Create an administrator

```bash
python manage.py createsuperuser
```

Enter a username, an email (optional) and a password. The password is hidden while you type. If Django warns that the password is too simple, you can type `y` to keep it for this workshop. Do not do this on a real site.

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

Refresh the admin page. A **Members** section appears with **Books**, **Members** and **Reading logs**. Click around. Notice that the readable text comes from each model's `__str__` method: "Alice Johnson read Dune by Frank Herbert".

### 4. Customize how each model looks

The plain registration works, but a `ModelAdmin` class gives you control. Replace `members/admin.py` with:

```python
from django.contrib import admin
from django.db.models import Avg

from .models import Book, Member, ReadingLog

admin.site.site_header = "Book Club Administration"
admin.site.site_title = "Book Club Admin"
admin.site.index_title = "Manage the club"


class ReadingLogInline(admin.TabularInline):
    model = ReadingLog
    extra = 1


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "favorite_book", "joined", "books_read")
    search_fields = ("name", "email")
    list_filter = ("joined",)
    date_hierarchy = "joined"
    inlines = [ReadingLogInline]

    @admin.display(description="Books read")
    def books_read(self, obj):
        return obj.readings.count()


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "genre", "pages", "published_year", "average_rating")
    list_filter = ("genre",)
    search_fields = ("title", "author")
    ordering = ("title",)
    fieldsets = (
        (None, {"fields": ("title", "author", "genre")}),
        ("Details", {"fields": ("pages", "published_year", "isbn"), "classes": ("collapse",)}),
    )
    inlines = [ReadingLogInline]

    @admin.display(description="Avg rating")
    def average_rating(self, obj):
        result = obj.readings.aggregate(avg=Avg("rating"))["avg"]
        return round(result, 1) if result else "-"


@admin.register(ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = ("member", "book", "date_finished", "rating", "would_recommend")
    list_filter = ("rating", "would_recommend", "date_finished")
    search_fields = ("member__name", "book__title")
    list_editable = ("rating", "would_recommend")
    autocomplete_fields = ("member", "book")
    date_hierarchy = "date_finished"
    actions = ["mark_recommended"]

    @admin.action(description="Mark selected readings as recommended")
    def mark_recommended(self, request, queryset):
        updated = queryset.update(would_recommend=True)
        self.message_user(request, f"{updated} reading(s) marked as recommended.")
```

The server reloads automatically. Refresh the admin.

**What each setting does**

| Setting | Effect |
|---|---|
| `list_display` | The columns in the list page. It can include methods, like `books_read` |
| `search_fields` | Adds a search box. `member__name` searches across a relationship |
| `list_filter` | Adds a filter sidebar |
| `date_hierarchy` | Adds date drill-down links at the top of the list |
| `list_editable` | Lets you edit fields directly in the list and save them all at once |
| `ordering` | The default sort order |
| `fieldsets` | Groups the fields on the edit form. `collapse` hides a group until clicked |
| `inlines` | Shows related rows on the same page, so you can add a member's reading logs on the member page |
| `autocomplete_fields` | Replaces a long dropdown with a search-as-you-type box |
| `actions` | Adds your own bulk action to the "Action" menu |
| `@admin.display` | Gives a method a readable column title |

### 5. Manipulate data from the admin

Work through these tasks. Each one shows a different part of the admin:

| Task | How | What to notice |
|---|---|---|
| **Add** a book | Books → **Add book** → fill in the form → **Save** | The genre is a dropdown (from `choices`). The "Details" group is collapsed |
| **Edit** a book | Click a title in the list, change `pages`, **Save** | The change appears in the list straight away |
| **Search** | In Books, type `tolkien` | Matches on `title` and `author` |
| **Filter** | In Books, click **Fantasy** in the sidebar | The list shrinks to matching rows |
| **Sort** | Click a column heading | Click again to reverse the order |
| **Add a log** | Reading logs → **Add reading log**; pick a member and a book | The member and book use search boxes |
| **Validation** | Enter a rating of `7` and save | The admin shows "Ensure this value is less than or equal to 5". Validators run here, unlike in `save()` |
| **Unique constraint** | Add a second log for the same member and book | The admin shows a friendly error instead of crashing |
| **Edit in the list** | In Reading logs, change a rating or tick **Would recommend** in the list, then **Save** | Several rows are updated at once |
| **Inline editing** | Open a member and use the **Reading logs** table at the bottom to add a log | You manage related data without leaving the page |
| **Bulk action** | In Reading logs, tick several rows, choose **Mark selected readings as recommended**, then **Go** | A message reports how many rows changed |
| **History** | Open any object and click **History** | Django records who changed what, and when |
| **Delete** | Add a test member with a reading log, then delete the member | The confirmation page lists the reading logs that will also be deleted. That is `on_delete=CASCADE` in action |

### 6. Compare with the shell

Everything you did in the admin could be done in the shell. Try this in `python manage.py shell` to see your admin edits:

```python
from members.models import ReadingLog
ReadingLog.objects.filter(would_recommend=True).count()
```

The admin and the shell use the same ORM and the same database.

### 7. Where the admin fits

The admin is built for the **site owner**, not for the public. It is quick for managing data, adding test content and fixing mistakes. For pages your members use, you write your own views and templates, as in the earlier parts.

### Checkpoint

- [ ] You can log in to `/admin/` and see Books, Members and Reading logs
- [ ] You added a book and a reading log from the admin
- [ ] An invalid rating or a duplicate log is rejected with a message
- [ ] You ran the bulk action and saw the success message

### Exercise

On the member detail page, show the books that member has read. In the `members/member_detail.html` template, use the reverse relationship. Hint:

```html
<h2>Books read</h2>
<ul>
  {% for reading in member.readings.all %}
    <li>{{ reading.book.title }} ({{ reading.rating|default:"-" }}/5)</li>
  {% empty %}
    <li>No books logged yet.</li>
  {% endfor %}
</ul>
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `no such table: members_book` | Run `python manage.py makemigrations members`, then `python manage.py migrate` |
| `makemigrations` says "No changes detected" | Save `models.py`, and check `"members"` is in `INSTALLED_APPS` |
| The red "unapplied migration(s)" warning | Run `python manage.py migrate` |
| `IntegrityError: UNIQUE constraint failed` | You created a duplicate (same email, same title and author, or same member and book) |
| `IntegrityError: NOT NULL constraint failed` | A required field has no value. Pass it, or give the field a `default`, or `null=True` |
| `Book matching query does not exist` | The title in `get()` is misspelled, or the book does not exist yet |
| `Cannot assign "1": must be a "Member" instance` | Pass the object (`member=alice`) and not an id. To use an id, write `member_id=1` |
| `You are trying to add a non-nullable field...` | Choose option 2, then add `default=...`, `blank=True` or `null=True` to the field |
| A model is missing from the admin | Register it in `members/admin.py` and save the file |
| `admin.E108` or `admin.E116` errors | A name in `list_display`, `list_filter` or `search_fields` does not exist on the model. Check spelling |
| `CSRF verification failed` on admin login (Codespaces) | Add the `CSRF_TRUSTED_ORIGINS` block from the Part II setup and restart the server |
| `InconsistentMigrationHistory` | In development only: delete `db.sqlite3` and run `python manage.py migrate` (this loses your data) |
| Lost your superuser after resetting the database | Run `python manage.py createsuperuser` again |