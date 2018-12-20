from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from models import UserProfile, AttendanceLog, ActiveDevice
import json
from datetime import datetime, timedelta
from django.utils import timezone
#from django.core.exceptions import ObjectDoesNotExist # for exception processing

# Create your views here.

# translate to japanese format for time objects
def date_fmt_ja(obj):
    date_ja = obj.strftime("%Y年%m月%d日")
    weekday_n = int((obj).strftime("%w"))
    weekday_s = ["日", "月", "火", "水", "木", "金", "土"]
    date_ja += "(" + weekday_s[weekday_n] + ") "
    date_ja += (obj).strftime("%X")
    return date_ja

@login_required
def index(request):

    user_id = request.user.id
    user_prof = UserProfile.objects.filter(user=user_id).select_related('user').get()
    print(user_prof)
    is_in_room = False
    time_enter = None
    available_users = []


    # 自分のステータスが在室中かどうかの確認処理
    if AttendanceLog.objects.filter(user=user_id).exists(): # 自分のレコードが存在するか

        if AttendanceLog.objects.filter(user=user_id, time_in__isnull=False, time_out__isnull=True).exists(): # 最も新しいレコードを取得

            is_in_room = True # つまり在室
            time_enter = AttendanceLog.objects.filter(user=user_id, time_in__isnull=False, time_out__isnull=True).select_related('user').latest('time_in')

        # 過去のレコードが存在しない場合は在室していないので初期値(is_in_room=False)のままクライアントに渡す


    # 在室者一覧取得のための処理
    if AttendanceLog.objects.exists(): # 全体でレコードが存在する場合

        if AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).exists():

            query = AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).select_related('user').all() # 現在の在室者一覧を取得

            for i in range(query.count()):
                time_in = date_fmt_ja(query[i].time_in)
                available_users.append({'username': query[i].user.name_ja, 'time_in': time_in})

        # 誰もいない場合は初期値(available_users=None)のままクライアントに返す

    # クライアント側に返すデータ
    params = {
        'title': 'ホーム',
        'username': user_prof.name_ja, # ユーザーの日本語名を代入
        'my_stat': is_in_room, # DB上の在室状況
        'time_in': time_enter,
        'all_stat': available_users,
    }

    return render(request, 'console/index.html', params)


@csrf_exempt
def request_from_browser(request):
    
    request_data = request.POST
    status_room = request_data.status
    user_id = request.user.id

    result = status_change(user_id, status_room)

    return JsonResponse(result)

@csrf_exempt
def request_from_log(request):

    request_data = request.POST
    status_connect = request_data.status # this variable should take a value either "connect", "disconnect" gior "outrange"
    username = request_data.user

    if UserProfile.objects.filter(user=username).exists():
        user_id = UserProfile.objects.filter(user=username).get(id)
    
    else:
        pass # create new user on Django App

    status_change(user_id, status_room)

def status_change(user_id, request_status): # user_id must be "int" type value, and request_status should be "bool" type value(True->Entering, False->Leaving)

    current_time = timezone.now()
    is_in_room = AttendanceLog.objects.filter(user=user_id, time_in__isnull=False, time_out__isnull=True).exists() # この関数が使われるのは

    if request_status and not is_in_room: # Entering the room
        log = AttendanceLog(user_id=user_id, time_in=current_time)
        log.save()

    elif not request_status and is_in_room: # Leaving the room
        log = AttendanceLog.objects.filter(user=user_id).latest('time_in')
        log.time_out = current_time
        log.save()

    
    else: # Return error message
        responce_data = {
            'status_proc': False, # False means process status is failed 
            'msg': 'The room status have not changed!',
        }
        return responce_data


    # Return success message
    responce_data = {
        'status_proc': True,
        'msg': 'The room status have successfully changed!'
    }
    return responce_data


@csrf_exempt
def status_all(request):

    request_data = request.POST
    available_users = []
    responce_data = {}

    #if AttendanceLog.objects.exists(): # 全体でレコードが存在する場合

    if AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).exists():

        query = AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).select_related('user') # 現在の在室者一覧を取得

        for i in range(query.count()):
            time_in = date_fmt_ja(query[i].time_in)
            available_users.append({'username': query[i].user.name_ja, 'time_in': time_in})


    # DB上の在室状況とリクエストの値が同じ場合エラーを返す
    else:
        responce_data = {
            'error': 'no record',
        }
        return JsonResponse(responce_data)


    # 問題ない場合はリクエストされた値をDBに代入しその値を返す
    responce_data = {
        'available_users': available_users,
    }
    print(responce_data)
    return JsonResponse(responce_data)


@csrf_exempt
def syslog(request):

    request_data = request.POST
    user_id = request_data['username']
    is_in_room = AttendanceLog.objects.filter(user=user_id).exists()
    is_first_time = ActiveDevice.objects.filter(user=user_id).exists()
    current_time = timezone.now()

    # 入室時の処理（データ整合性の確認のため、条件に２つの式を指定している）

    if request_data.status is 'connect':
        if is_first_time:
            device = ActiveDevice(user=user_id, device=request_data.mac_addr)
            device.save()
            if not is_in_room:


            query = ActiveDevice.objects.filter(user=user_id).select_related('user')
            mac_addr_list = [x.strip() for x in query.device.split(",")]
            for addr in mac_addr_list:
                if addr == request_data.mac_addr:
                    pass
        else:

    return None
