from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile, AttendanceLog, InRoom
import json
from datetime import datetime
# Create your views here.

@login_required
def index(request):
    user = request.user.id
    #print(all_user)
    user_prof = UserProfile.objects.filter(user=user).select_related('user').get()
    #query_username = UserProfile.objects.filter(user=user).values('name_ja')
    #print(username)
    #print(request.user.username)
    #type(username)
    #print(InRoom.objects.filter(user=user).values())
    #print(InRoom.objects.filter(user=user).get().available)
    my_status = AttendanceLog.objects.filter(user=user).select_related('user').latest('time_in')
    all_status = AttendanceLog.objects.filter(time_out__isnull=True).select_related('user').all()
    is_in_room = False

    if my_status.time_in and my_status.time_out is None:
        is_in_room = True # つまり在室

    params = {
        'title':'ホーム',
        'username': user_prof.name_ja, # ユーザーの日本語名を代入
        'my_stat': is_in_room, # DB上の在室状況
        'time_in': my_status.time_in,
        'all_stat': all_status
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
    my_status = AttendanceLog.objects.filter(user=user).select_related('user').latest('time_in')
    time = datetime.now().isoformat()
    #print(time)

    # DB上の在室状況とリクエストの値が同じ場合エラーを返す

    is_in_room = False

    if my_status.time_in and my_status.time_out is None:
        is_in_room = True # つまり在室

    #print(in_room, request_data['status'])
    if request_data['status'] is is_in_room: # 本来はDBないの値を持って来ないといけない
        responce_data = {
            'error':'not_changed'
        }
        return JsonResponse(responce_data)
    # 問題ない場合はリクエストされた値をDBに代入しその値を返す

    # 退出時の処理（データ整合性の確認のため、条件に２つの式を指定している）
    elif is_in_room is True and request_data['status'] is not is_in_room:
        #print(AttendanceLog.objects.filter(user=user).latest('time_in'))
        log = AttendanceLog.objects.filter(user=user).latest('time_in')
        log.time_out = time
        log.save()
        #InRoom.objects.filter(user=user).update(available=False)

        #time = datetime.now(timezone('Asia/Tokyo')).isoformat()
    # 入室時の処理
    elif is_in_room is False and request_data['status'] is not is_in_room:
        log = AttendanceLog(user_id=user, time_in=time)
        log.save()
        #InRoom.objects.filter(user=user).update(available=True)


    if my_status.time_in and my_status.time_out is None:
        is_in_room = True # つまり在室
    else:
        is_in_room = False

    responce_data = {
        'status': is_in_room
    }
    return JsonResponse(responce_data)

@login_required
def status_all(request):
    user = request.user.id
    user_prof = UserProfile.objects.filter(user=user).select_related('user').get()
    #data = Article.objects.select_related('UserProfile').filter(time_out__isnull=True)
    #print(data)
    data = AttendanceLog.objects.filter(time_out__isnull=True).select_related('user').all()
    #print(data.user.name_ja)
    #is_in_room = InRoom.objects.all().values('available')
    print(data)
    #data = [all_user, is_in_room]
    #print(data)
    params = {
        'title': '在室者一覧',
        'username': user_prof.name_ja,
        'data': data
        #'all_user': all_user,
        #'available': is_in_room
        }
    return render(request, 'console/status_all.html', params)

'''
def schedule(request):
    params = {
        'title':'本日の予定',
        'name_jp':'東　昭太朗',
        'status' : 1
        }
    return render(request, 'console/index.html', params)
'''
