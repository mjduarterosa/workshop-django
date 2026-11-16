from django.urls import path, re_path
from . import views
from django.views.generic import RedirectView

app_name = "members"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("people/", RedirectView.as_view(pattern_name="members:list"), name="people"),
    path("members/", views.MemberListView.as_view(), name="list"),
    path("members/<int:pk>/", views.MemberDetailView.as_view(), name="detail"),
    # path("members/", views.member_list, name="list"),
    # path("members/<int:member_id>", views.member_detail, name="detail"),
    path("hello/<str:name>/", views.hello, name="hello"),
    path("info/", views.request_info, name="info"),
    re_path(
        r"^members/archive/(?P<year>[0-9]{4})/$",
        views.members_by_year,
        name="archive-month",
    ),
    re_path(
        r"^members/initial/(?P<letter>[A-Za-z])/$",
        views.members_by_initial,
        name="initial",
    ),
]
