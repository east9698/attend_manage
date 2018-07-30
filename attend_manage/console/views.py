from django.shortcuts import render
from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def index(request):
    params = {
        'title':'ホーム',
        'name_jp':'東　昭太朗', # ユーザーの日本語名を代入
        'status':True, # DB上の在室状況
        }
    return render(request, 'console/index.html', params)

@csrf_exempt
def status_change(request):
    #request_json = request.POST['data'] # Ajaxリクエストとして取得したJSONデータを格納
    #request_data = json.loads(request_json) # JSONデータを辞書型に変換
    print(request.POST) # 送られてくるデータの中身を確認することは大切なこと！
    request_data = request.POST
    # DB上の在室状況とリクエストの値が同じ場合エラーを返す
    if request_data['status'] == 'enter': # 本来はDBないの値を持って来ないといけない
        responce_data = {
            'error':'not_changed'
        }
        return JsonResponse(responce_data)
    # 問題ない場合はリクエストされた値をDBに代入しその値を返す
    # data['status'] = models.------
    responce_data = {
        'status': request_data['status'],
    }
    return JsonResponse(responce_data)

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
