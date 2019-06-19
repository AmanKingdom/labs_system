from django.db import models
from apps.apply_experiments.models import Experiment


# 已有安排的实验室及其时间，时间通过实验的id从实验项目中获取
class Schedule(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'schedule'

    labs = models.CharField(max_length=20, verbose_name='实验室名称')
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, verbose_name='审核通过了的实验项目')

    def __str__(self):
        return self.labs
