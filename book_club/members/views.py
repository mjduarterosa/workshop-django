from django.shortcuts import render
from django.http import HttpResponse


def members(request):
    return HttpResponse("Hello World!")


def home(request):
    return HttpResponse("Welcome to the Book Club!")


def hello(request, name):
    return HttpResponse(f"Hello, {name}! Welcome to the Book Club!")
