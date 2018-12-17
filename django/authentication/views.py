from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site
from django.views import generic
from .forms import LoginForm

class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'auth/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context.update({
            self.redirect_field_name: self.get_redirect_url(),
            'site': current_site,
            'site_name': current_site.name,
            'title': 'ログイン',
            **(self.extra_context or {})
        })
        return context



class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'auth/logout.html'


@csrf_exempt
def radius(request):

    request_data = request.POST
    print(request_data)
    user_id = request.user.id
    current_time = datetime.now().isoformat()

    def is_available():
        return AttendanceLog.objects.filter(user=user_id).exists()

    def is_in_room():
        return AttendanceLog.objects.filter(user=user_id, time_in__isnull=False, time_out__isnull=True).exists()


    # ログイン経験があり、入室状態の場合
    if is_available() is True and is_in_room() is True:
        pass

    # ログイン経験はあるが、未入室状態の場合
    elif is_available() is True and is_in_room() is False:
        from ..console.models import AttendanceLog
        log = AttendanceLog(user_id=user_id, time_in=current_time)
        log.save()
    '''
        # ログイン経験がなく、Djangoのシステムにアカウントが存在しない場合
        elif is_available() is False:

            user =
            log = AttendanceLog.objects.filter(user=user_id).latest('time_in')
            log.time_out = current_time
            log.save()

    '''

    return 0
