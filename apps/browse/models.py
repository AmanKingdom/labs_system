from django.db import models
from apps.apply_experiments.models import Experiment


# 已有安排的实验室及其时间，时间通过实验的id从实验项目中获取
from apps.super_manage.models import Classes, Teacher


class Schedule(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'schedule'

    labs = models.CharField(max_length=20, verbose_name='实验室名称')
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, verbose_name='审核通过了的实验项目')

    def __str__(self):
        return self.labs


# 学生助理
class Assistant(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'assistant'

    name = models.CharField(max_length=20, verbose_name='助理姓名')
    account = models.CharField(max_length=100, verbose_name='账号')
    password = models.CharField(max_length=18, verbose_name='登录密码', default='123456')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='协助的教师')

    def __str__(self):
        return self.name
