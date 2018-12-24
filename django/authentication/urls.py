from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', views.Login.as_view(), name='login'), # customized
    path('logout/', LogoutView.as_view(), name='logout'), # use default template
]
