from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says hey there world!<br/> <a href='/rango/about'>About</a>")

def about(request):
	return HttpResponse("Rango says here is the about page. <p> This tutorial has been put together by Jaakko Alasuvanto, 2160057 <br/> <a href='/rango'> Index </a>")