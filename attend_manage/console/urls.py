from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('status_all/', views.status_all, name='status_all'),
    path('schedule/', views.schedule, name='schedule'),
]
