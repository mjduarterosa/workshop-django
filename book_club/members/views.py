from django.shortcuts import render
from django.http import HttpResponse


def members(request):
    return HttpResponse("Hello World!")


def home(request):
    return HttpResponse("Welcome to the Book Club!")


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
