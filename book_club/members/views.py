from django.shortcuts import render
from django.http import HttpResponse
from .models import Member
from django.views.generic import DetailView, ListView, TemplateView


class MemberListView(ListView):
    model = Member
    template_name = "members/member_list.html"
    context_object_name = "members"


class MemberDetailView(DetailView):
    model = Member
    template_name = "members/member_detail.html"
    context_object_name = "member"


class AboutView(TemplateView):
    template_name = "members/about.html"


def members(request):
    return HttpResponse("Hello World!")


def home(request):
    return render(request, "members/home.html")


def hello(request, name):
    return HttpResponse(f"Hello, {name}! Welcome to the Book Club!")


def request_info(request):
    name = request.GET.get("name", "stranger")
    text = (
        f"Method: {request.method}\n"
        f"Path: {request.path}\n"
        f"Hello, {name}!"
    )
    return HttpResponse(text, content_type="text/plain")


# def member_list(request):
#    members = Member.objects.all()
#    return render(request, "members/member_list.html", {"members": members})


# def member_detail(request, member_id):
#    try:
#        member = Member.objects.get(pk=member_id)
#    except Member.DoesNotExist:
#        return render(
#            request,
#            "members/member_not_found.html",
#            {"member_id": member_id},
#            status=404,
#        )
#    return render(request, "members/member_detail.html", {"member": member})


def members_by_year(request, year):
    members = Member.objects.filter(joined_date__year=int(year))
    return render(request, "members/member_list.html", {"members": members})


def members_by_initial(request, letter):
    members = Member.objects.filter(firstname__istartswith=letter)
    return render(request, "members/member_list.html", {"members": members})
