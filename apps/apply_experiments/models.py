from django.db import models
from apps.super_manage.models import Institute, Course


# 实验类型
class ExperimentType(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'experiment_type'

    name = models.CharField(max_length=30, verbose_name='实验类型')

    def __str__(self):
        return self.name


# 实验室
class Labs(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'labs'

    name = models.CharField(max_length=30, verbose_name='实验室名称')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='所属学院')
    number_of_people = models.IntegerField(verbose_name='容纳人数', default=40)
    dispark = models.BooleanField(verbose_name='开放情况', default=True)

    def __str__(self):
        return self.name


# 单项实验的特殊需求
class SpecialRequirements(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'special_requirements'

    special_consume_requirements = models.CharField(max_length=100, verbose_name='特殊耗材需求', null=True, blank=True)
    special_system_requirements = models.CharField(max_length=100, verbose_name='特殊系统需求', null=True, blank=True)
    special_soft_requirements = models.CharField(max_length=100, verbose_name='特殊软件需求', null=True, blank=True)


# 实验项目
class Experiment(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'experiment'

    name = models.CharField(max_length=50, verbose_name='实验项目名称')
    experiment_type = models.ForeignKey(ExperimentType, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='实验类型')
    lecture_time = models.IntegerField(verbose_name='学时')
    which_week = models.IntegerField(verbose_name='周次(哪周上课？)')
    days_of_the_week = models.IntegerField(verbose_name='星期')
    section = models.IntegerField(verbose_name='节次')
    labs = models.ForeignKey(Labs, on_delete=models.SET_NULL, null=True, verbose_name='实验室')
    special_requirements = models.ForeignKey(SpecialRequirements, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='特殊需求')
    lesson = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='所属课程名称')
    status = models.IntegerField(verbose_name='状态，0-草稿状态，1-已提交但未审核状态，2-已提交但审核未通过状态，4-审核通过状态', default=0)

    def __str__(self):
        return self.name
