from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 参照先のレコードが削除されるとこちらも連動して削除される
    name_ja = models.CharField(max_length=50)

    def __str__(self):
        return 'id: %s, 表示名: %s' % (self.user, self.name_ja)

class AttendanceLog(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT) # このテーブル上のレコードが削除されても参照先のテーブルからユーザ情報を削除しない
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)


    def __str__(self):

        from .views import date_fmt_ja

        if self.time_out:
            return '%s(%s): 入室 %s / 退室 %s' % (self.user.name_ja, self.user.user.username, date_fmt_ja(self.time_in), date_fmt_ja(self.time_out))
        else :
            return '%s(%s): 入室 %s / 退室 %s' % (self.user.name_ja, self.user.user.username, date_fmt_ja(self.time_in), self.time_out)
'''
class RoomBBS(models.Model):
    auther = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    comment = models.CharField(max_length=200)

    def __str__(self):
        return '%s(%s): %s' % (self.auther.name_ja, self.auther, self.comment)
'''
