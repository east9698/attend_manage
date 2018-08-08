from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 参照先のレコードが削除されるとこちらも連動して削除される
    name_ja = models.CharField(max_length=50)

    def __str__(self):
        return '%s %s' % (self.user, self.name_ja)

class AttendanceLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT) # このテーブル上のレコードが削除されても参照先のテーブルからユーザ情報を削除しない
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s : %s / %s' % (self.user, self.time_in, self.time_out)

class InRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    available = models.BooleanField()

    def __str__(self):
        return '%s %s' % (self.user, self.available)

class RoomBBS(models.Model):
    auther = models.Foreignkey(User, on_delete=models.PROTECT)
    comment = models.CharField(max_length=200)
