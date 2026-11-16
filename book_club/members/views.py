from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Member


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


def member_list(request):
    members = Member.objects.all()
    return render(request, "members/member_list.html", {"members": members})


def member_detail(request, member_id):
    try:
        member = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        return render(
            request,
            "members/member_not_found.html",
            {"member_id": member_id},
            status=404,
        )
    return render(request, "members/member_detail.html", {"member": member})
