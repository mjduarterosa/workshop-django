from django.urls import path
from . import views

app_name = "members"

urlpatterns = [
    path("", views.home, name="home"),
    path("members/", views.member_list, name="list"),
    path("members/<int:member_id>", views.member_detail, name="detail"),
    path("hello/<str:name>/", views.hello, name="hello"),
    path("info/", views.request_info, name="info"),
]
