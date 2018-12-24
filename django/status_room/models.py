from django.db import models
from django.conf import settings
# Create your models here.

#from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class AttendanceLog(models.Model):
    #usermodel = get_user_model()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT) # このテーブル上のレコードが削除されても参照先のテーブルからユーザ情報を削除しない
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        from .views import date_fmt_ja
        if self.time_out:
            return '%s(%s): 入室 %s / 退室 %s' % (self.user.get_full_name(), self.user.username, date_fmt_ja(self.time_in), date_fmt_ja(self.time_out))
        else :
            return '%s(%s): 入室 %s / 退室 %s' % (self.user.get_full_name(), self.user.username, date_fmt_ja(self.time_in), self.time_out)


class ActiveDevice(models.Model):
    #usermodel = get_user_model()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    device = models.TextField(name="mac_addr")

    def __str__(self):
        return '%s(%s): %s' % (self.user.get_full_name(), self.user.username, self.device)
