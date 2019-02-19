from django.shortcuts import render # , redirect, resolve_url
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import AttendanceLog, ActiveDevice
import json
# from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from distutils.util import strtobool
from authentication.forms import *
from django.db.models import DurationField, ExpressionWrapper, F, Sum

# translate into japanese format for time objects
def date_fmt_ja(obj):
    date_ja = obj.strftime("%Y年%m月%d日")
    weekday_n = int(obj.strftime("%w"))
    weekday_s = ["日", "月", "火", "水", "木", "金", "土"]
    date_ja += "(" + weekday_s[weekday_n] + ") "
    date_ja += obj.strftime("%X")
    return date_ja

@login_required
def index(request):
    usermodel = get_user_model()
    user = request.user.username
    user_prof = usermodel.objects.filter(username=user).get()

    is_in_room = False
    time_enter = None
    available_users = []
    durations = []
    print(user_prof.username)

    # if not user_prof.is_active():
    #     pass

    # 自分のステータスが在室中かどうかの確認処理
    if AttendanceLog.objects.filter(user=user).exists(): # 自分のレコードが存在するか

        if AttendanceLog.objects.filter(user=user, time_in__isnull=False, time_out__isnull=True)\
                .exists(): # 最も新しいレコードを取得

            is_in_room = True # つまり在室
            time_enter = AttendanceLog.objects.filter(user=user, time_in__isnull=False, time_out__isnull=True)\
                    .select_related('user').latest('time_in')

        # 過去のレコードが存在しない場合は在室していないので初期値(is_in_room=False)のままクライアントに渡す

    # 在室者一覧取得のための処理
    if AttendanceLog.objects.exists(): # 全体でレコードが存在する場合

        if AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).exists():

            query = AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True)\
                    .select_related('user').all() # 現在の在室者一覧を取得

            for q in query:
                time_in = date_fmt_ja(q.time_in)
                available_users.append({
                    'username': q.user.get_name_ja() if q.user.get_name_ja() else q.user.username,
                    'time_in': time_in,
                })

        # 誰もいない場合は初期値(available_users=None)のままクライアントに返す

        duration = AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=False).values('user_id').annotate(duration=Sum(ExpressionWrapper(F('time_out') - F('time_in'), output_field=DurationField())))

        for d in duration:
            durations.append({
                'username': d['user_id'],
                'duration': int(d['duration'].total_seconds()),
            })
        #diff = AttendanceLog.objects.annotate(duration=ExpressionWrapper(F('time_out') - F('time_in'), output_field=DurationField())) # for debug
        print(duration)

    # クライアント側に返すデータ
    params = {
        'title': 'ホーム',
        'username': user_prof.get_name_ja() if user_prof.get_name_ja() else user_prof.username, # ユーザーの日本語名を代入（未登録の場合はユーザーネームを）
        'my_stat': is_in_room, # DB上の在室状況
        'time_in': time_enter,
        'all_stat': available_users,
        'duration_all': durations,
    }

    return render(request, 'status_room/index.html', params)


class UserCreationView():

    form = UserCreationForm

@csrf_exempt
def request_from_browser(request):

    usermodel = get_user_model()
    request_data = request.POST
    print(request) # for debug
    status_room = bool(strtobool(request_data['status']))
    print(status_room) # for debug
    user = request.user.username
    userobj = usermodel.objects.filter(username=user).first()

    result = status_change(userobj, status_room)

    return JsonResponse(result)

'''
def get_staying_time():
    #User = get_user_model
    #amount_of_user = User.objects.all(user).count()
    #print(amount_of_user)
    query = AttendanceLog.objects.annotate(duration=ExpressionWrapper(F('time_out') - F('time_in'), output_field=DurationField()))
    #query = AttendanceLog.objects.filter(user=user, time_in__isnull=False, time_out__isnull=False).select_related('user').all()
    print(query)
'''

@csrf_exempt
def request_from_log(request):

    from authentication.models import User
    usermodel = get_user_model()
    request_data = json.loads(request.body)
    request_device = request_data['mac_addr']
    status_connect = request_data['status']

    try:
        user = request_data['username']

        try:
            userobj = usermodel.objects.get(username=user)
        except User.DoesNotExist:
            userobj = usermodel(username=user)
            userobj.save()

        if not ActiveDevice.objects.filter(user=user).exists():  # create new user on Django App
            # userobj = usermodel.objects.filter(username=user).get()
            device = ActiveDevice(user=userobj, mac_addr="")
            device.save()
        if status_connect:
            register_device(user, request_device)
    except KeyError:
        if not status_connect: unregister_device(request_device)

    return HttpResponse()

def register_device(username, request_device):  # process for connect association
    usermodel = get_user_model()
    record = ActiveDevice.objects.filter(user=username).get()

    if ActiveDevice.objects.filter(user=username).values('mac_addr'):
        mac_addr_list = {addr.strip() for addr in record.mac_addr.split(",")}  # convert str to set(dict)
        mac_addr_list = set(filter(lambda x:x != "", mac_addr_list))  # remove empty element

    if not(set(request_device) <= mac_addr_list):
        mac_addr_list.add(request_device)
        record.mac_addr = ",".join(map(str, mac_addr_list))
        record.save()

    userobj = usermodel.objects.filter(username=record.user.username).get()
    status_change(userobj, True)


def unregister_device(request_device): # process for disconnection

    usermodel = get_user_model()

    if ActiveDevice.objects.filter(mac_addr__icontains=request_device).exists():

        record = ActiveDevice.objects.filter(mac_addr__icontains=request_device).get()
        mac_addr_list = {addr.strip() for addr in record.mac_addr.split(",")}  # convert str to set(dict)
        mac_addr_list = set(filter(lambda x:x != "", mac_addr_list))  # remove empty element


        if not(set(request_device) <= mac_addr_list):
            mac_addr_list.remove(request_device)
            record.mac_addr = ",".join(map(str, mac_addr_list))
            record.save()

        if not mac_addr_list:
            userobj = usermodel.objects.filter(username=record.user.username).get()
            status_change(userobj, False)


def status_change(username, request_status): # request_status should be "bool" type value(True->Entering, False->Leaving)

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

    # request_data = request.POST
    available_users = []
    # responce_data = {}

    # if AttendanceLog.objects.exists(): # 全体でレコードが存在する場合

    if AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).exists():

        query = AttendanceLog.objects.filter(time_in__isnull=False, time_out__isnull=True).select_related('user') # 現在の在室者一覧を取得
        print(query.count())
        print(query)
        print(query.count())
        """
        for i in list(range(query.count())):
            print("{0}-{1}".format(i, query[i].user.username))

            time_in = date_fmt_ja(query[i].time_in)
        """
        print([q for q in query])
        for q in query:
            print("---{0}".format(q.user.username))

            time_in = date_fmt_ja(q.time_in)

            if q.user.get_name_ja():
                available_users.append({'username': q.user.get_name_ja(), 'time_in': time_in})
            else:
                available_users.append({'username': q.user.username, 'time_in': time_in})

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
