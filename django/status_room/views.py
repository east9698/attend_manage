from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import AttendanceLog, ActiveDevice
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from distutils.util import strtobool

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
    usermodel = get_user_model()
    user = request.user.username
    user_prof = usermodel.objects.filter(username=user).get()
    print(user_prof)
    is_in_room = False
    time_enter = None
    available_users = []


    # 自分のステータスが在室中かどうかの確認処理
    if AttendanceLog.objects.filter(user=user).exists(): # 自分のレコードが存在するか

        if AttendanceLog.objects.filter(user=user, time_in__isnull=False, time_out__isnull=True).exists(): # 最も新しいレコードを取得

            is_in_room = True # つまり在室
            time_enter = AttendanceLog.objects.filter(user=user, time_in__isnull=False, time_out__isnull=True).select_related('user').latest('time_in')

        # 過去のレコードが存在しない場合は在室していないので初期値(is_in_room=False)のままクライアントに渡す


    # 在室者一覧取得のための処理
    if AttendanceLog.objects.exists(): # 全体でレコードが存在する場合

        if AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).exists():

            query = AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).select_related('user').all() # 現在の在室者一覧を取得

            for i in range(query.count()):
                time_in = date_fmt_ja(query[i].time_in)
                available_users.append({'username': query[i].user.get_name_ja(), 'time_in': time_in})

        # 誰もいない場合は初期値(available_users=None)のままクライアントに返す

    # クライアント側に返すデータ
    params = {
        'title': 'ホーム',
        'username': user_prof.get_name_ja(), # ユーザーの日本語名を代入
        'my_stat': is_in_room, # DB上の在室状況
        'time_in': time_enter,
        'all_stat': available_users,
    }

    return render(request, 'status_room/index.html', params)


@csrf_exempt
def request_from_browser(request):
    
    usermodel = get_user_model()
    request_data = request.POST
    status_room = bool(strtobool(request_data['status']))
    print(status_room)
    user = request.user.username
    userobj = usermodel.objects.filter(username=user).first()

    result = status_change(userobj, status_room)

    return JsonResponse(result)


@csrf_exempt
def request_from_log(request):

    usermodel = get_user_model()
    request_data = request.POST
    request_device = request_data['mac_addr']
    status_connect = request_data['status'] # this variable should take a value either "connect", "disconnect" gior "outrange"
    user = request_data['username']

    if not usermodel.objects.filter(username=user).exists(): # create new user on Django App
        
        account = usermodel(username=user, password=None)
        account.is_active = False
        account.save()

        device = ActiveDevice(user=user, device=None)
        device.save()


    status_change(user, status_connect)
    register_device(user, status_connect, request_device)


def status_change(username, request_status): # user_id must be "int" type value, and request_status should be "bool" type value(True->Entering, False->Leaving)

    current_time = timezone.now()
    is_in_room = AttendanceLog.objects.filter(user=username, time_in__isnull=False, time_out__isnull=True).exists()

    if request_status and not is_in_room: # Entering the room
        log = AttendanceLog(user=username, time_in=current_time)
        log.save()

    elif not request_status and is_in_room: # Leaving the room
        log = AttendanceLog.objects.filter(user=username).latest('time_in')
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

    #request_data = request.POST
    available_users = []
    responce_data = {}

    #if AttendanceLog.objects.exists(): # 全体でレコードが存在する場合

    if AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).exists():

        query = AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).select_related('user') # 現在の在室者一覧を取得

        for i in range(query.count()):
            time_in = date_fmt_ja(query[i].time_in)
            available_users.append({'username': query[i].user.get_name_ja(), 'time_in': time_in})


    # DB上の在室状況とリクエストの値が同じ場合エラーを返す
    else:
        responce_data = {
            'status_proc': True,
            'available_users': None,
            'msg': 'There are no available users.',
        }
        return JsonResponse(responce_data)


    # 問題ない場合はリクエストされた値をDBに代入しその値を返す
    responce_data = {
        'status_proc': True,
        'available_users': available_users,
        'msg': 'success',
    }
    print(responce_data)
    return JsonResponse(responce_data)


def register_device(username, request_status, request_device):

    #usermodel = get_user_model()
    #is_registerd = usermodel.objects.filter(user=username).exists()
    #is_first_time = ActiveDevice.objects.filter(user=username).exists() # ユーザー作成時に自動生成するようにすれば不要になる
    current_time = timezone.now()

    record = ActiveDevice.objects.filter(user=username).first()
    mac_addr_list = set([addr.strip() for addr in record.device.split(",")])

    # process for connect association
    if request_status:

        if not(set(request_device) <= mac_addr_list):
            mac_addr_list.add(request_device)

        if not mac_addr_list.__len__:
            log = AttendanceLog(user=username, time_in=current_time)
            log.save()


    # process for disconnection
    elif not request_status:

        if (set(request_device) <= mac_addr_list):
            mac_addr_list.remove(request_device)

        if not mac_addr_list.__len__:
            log = AttendanceLog.objects.filter(user=username).latest('time_in')
            log.time_out = current_time
            log.save()

    result_str = ",".join(mac_addr_list)
    record.device = result_str
    record.save()