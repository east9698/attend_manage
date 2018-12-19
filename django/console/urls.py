from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('status_change/', views.status_change, name='status_change'), # for ajax in index.html
    path('status_all/', views.status_all, name='status_all'),
    #path('schedule/', views.schedule, name='schedule'),
    path('radius/', views.radius, name='radius'),
    path('syslog/', views.syslog, name='syslog'),

]
