from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    params = {
        'title':'ホーム',
        'name_jp':'東　昭太朗',
        'status':True,
        }
    return render(request, 'console/index.html', params)

def status_change(request):
    params = {
        'title':'ホーム',
        'name_jp':'東　昭太朗',
        'status':True,
        }
    return render(request, 'console/index.html', params)

def status_all(request):
    params = {
        'title':'研究室の今',
        'name_jp':'東　昭太朗',
        'status' : 0
        }
    return render(request, 'console/index.html', params)

def schedule(request):
    params = {
        'title':'本日の予定',
        'name_jp':'東　昭太朗',
        'status' : 1
        }
    return render(request, 'console/index.html', params)
