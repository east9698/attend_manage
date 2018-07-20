from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    params = {
        'name_jp':'東　昭太朗',
        'status' : True,
        }
    return render(request, 'console/index.html', params)
