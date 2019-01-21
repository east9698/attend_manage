from django.shortcuts import resolve_url  # , render
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView # , LogoutView
#from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site
from django.views import generic
from .forms import *



class Login(LoginView):
    """ログインページ"""
    form_class = AuthenticationForm
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

class UserUpdateView(generic.edit.UpdateView):
    model = get_user_model()
    form_class = UserChangeForm
    template_name = 'update.html'

    def get_success_url(self):
        return resolve_url('room:index', pk=self.kwargs['pk'])

'''
class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'auth/login.html'
'''
