from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'), # customized
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # use default template
    #path('radius_rec/', views.radius_rec, name='radius_rec'), # record radius auth log

]
