from django.contrib import admin
from .models import Book, Member, ReadingLog

admin.site.register(Member)
admin.site.register(Book)
admin.site.register(ReadingLog)
