from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserDetail, AttendanceLog, InRoom
import json
from datetime import datetime
# Create your views here.

@login_required
def index(request):
    user = request.user.id
    #print(all_user)
    username = UserDetail.objects.filter(id=user).get().name_ja
    #query_username = UserDetail.objects.filter(user=user).values('name_ja')
    #print(username)
    #print(request.user.username)
    #type(username)
    #print(InRoom.objects.filter(user=user).values())
    #print(InRoom.objects.filter(user=user).get().available)
    status = InRoom.objects.filter(user=user).get().available

    params = {
        'title':'ホーム',
        'username': username, # ユーザーの日本語名を代入
        'status': status, # DB上の在室状況
        }
    return render(request, 'console/index.html', params)

@csrf_exempt
def status_change(request):
    #request_json = request.POST['data'] # Ajaxリクエストとして取得したJSONデータを格納
    #request_data = json.loads(request_json) # JSONデータを辞書型に変換
    #print('request_data')
    #print(request.POST) # 送られてくるデータの中身を確認することは大切なこと！
    request_data = request.POST
    user = request.user.id
    in_room = InRoom.objects.filter(user=user).get().available
    time = datetime.now().isoformat()
    #print(time)

    # DB上の在室状況とリクエストの値が同じ場合エラーを返す
    #print(in_room, request_data['status'])
    if request_data['status'] == in_room: # 本来はDBないの値を持って来ないといけない
        responce_data = {
            'error':'not_changed'
        }
        return JsonResponse(responce_data)
    # 問題ない場合はリクエストされた値をDBに代入しその値を返す

    # 退出時の処理（データ整合性の確認のため、条件に２つの式を指定している）
    elif request_data['status'] == 'exit' and in_room == True:
        #print(AttendanceLog.objects.filter(user=user).latest('time_in'))
        log = AttendanceLog.objects.filter(user=user).latest('time_in')
        log.time_out = time
        log.save()
        InRoom.objects.filter(user=user).update(available=False)

        #time = datetime.now(timezone('Asia/Tokyo')).isoformat()
    # 入室時の処理
    elif request_data['status'] == 'enter':
        log = AttendanceLog(user_id=user, time_in=time)
        log.save()
        InRoom.objects.filter(user=user).update(available=True)

    responce_data = {
        'status': InRoom.objects.filter(user=user).get().available,
    }
    return JsonResponse(responce_data)

@login_required
def status_all(request):
    user = request.user.id

    #data = Article.objects.select_related('UserDetail').filter(time_out__isnull=True)
    print(data)
    all_user = AttendanceLog.select_related('User')
    print(all_user)
    is_in_room = InRoom.objects.all().values('available')
    print(is_in_room)
    #data = [all_user, is_in_room]
    #print(data)
    params = {
        'title': '研究室の今',
        'name_ja': UserDetail.objects.filter(user=user).values('name_ja'),
        'data': data
        #'all_user': all_user,
        #'available': is_in_room
        }
    return render(request, 'console/index.html', params)

'''
def schedule(request):
    params = {
        'title':'本日の予定',
        'name_jp':'東　昭太朗',
        'status' : 1
        }
    return render(request, 'console/index.html', params)
'''
