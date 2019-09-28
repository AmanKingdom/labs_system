from django.db import models
from apps.super_manage.models import Teacher


# 学生助理
class Assistant(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'assistant'

    name = models.CharField(max_length=20, verbose_name='助理姓名')
    account = models.CharField(max_length=100, verbose_name='账号')
    password = models.CharField(max_length=18, verbose_name='登录密码', default='123456')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='协助的教师')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return self.name
