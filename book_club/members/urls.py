from django.urls import path
from . import views

urlpatterns = [
    path("members/", views.members, name="members"),
    path("", views.home, name="home"),
    path("hello/<str:name>/", views.hello, name="hello")
]
