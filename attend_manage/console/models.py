from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 参照先のレコードが削除されるとこちらも連動して削除される
    name_ja = models.CharField(max_length=50)

class AttendanceLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT) # このテーブル上のレコードが削除されても参照先のテーブルからユーザ情報を削除しない
    time_in = models.DateTimeField()
    time_out = models.DateTimeField()

class InRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    available = models.BooleanField()
