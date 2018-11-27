from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile, AttendanceLog
import json
from datetime import datetime, timedelta
from django.utils import timezone

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
def status_change(request):

    request_data = request.POST
    user_id = request.user.id
    is_in_room = AttendanceLog.objects.filter(user=user_id, time_in__isnull=False, time_out__isnull=True).exists() # この関数が使われるのは
    current_time = timezone.now()


    # 退出時の処理（データ整合性の確認のため、条件に２つの式を指定している）
    if is_in_room is True and request_data['status'] is not is_in_room:
        log = AttendanceLog.objects.filter(user=user_id).latest('time_in')
        log.time_out = current_time
        log.save()

    # 入室時の処理
    elif is_in_room is False and request_data['status'] is not is_in_room:
        log = AttendanceLog(user_id=user_id, time_in=current_time)
        log.save()

    # DB上の在室状況とリクエストの値が同じ場合エラーを返す
    elif request_data['status'] is is_in_room:
        responce_data = {
            'error':'same status(no change)'
        }
        return JsonResponse(responce_data)


    # 問題ない場合はリクエストされた値をDBに代入しその値を返す
    responce_data = {
        'status': is_in_room
    }
    return JsonResponse(responce_data)

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
def radius(request):

    request_data = request.POST
    user_id = request_data['username']
    is_in_room = AttendanceLog.objects.filter(user=user_id, time_in__isnull=False, time_out__isnull=True).exists() # この関数が使われるのは
    current_time = timezone.now()

    # 入室時の処理（データ整合性の確認のため、条件に２つの式を指定している）
    if is_in_room is False:
        log = AttendanceLog(user_id=user_id, time_in=current_time)
        log.save()

    return None
