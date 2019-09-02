from django.db import models
from apps.super_manage.models import Institute, Course, Labs, LabsAttribute


# 实验类型
class ExperimentType(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'experiment_type'

    name = models.CharField(max_length=30, verbose_name='实验类型')

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

    no = models.IntegerField(verbose_name='编号', blank=True, null=True)
    name = models.CharField(max_length=50, verbose_name='实验项目名称')
    experiment_type = models.ForeignKey(ExperimentType, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='实验类型')
    lecture_time = models.IntegerField(verbose_name='学时')
    which_week = models.IntegerField(verbose_name='周次(哪周上课？)')
    days_of_the_week = models.IntegerField(verbose_name='星期')
    section = models.IntegerField(verbose_name='节次')
    labs = models.ManyToManyField(Labs, verbose_name='实验室')
    special_requirements = models.ForeignKey(SpecialRequirements, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='特殊需求')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='所属课程')
    status = models.IntegerField(verbose_name='状态，0-草稿状态，1-已提交但未审核状态，2-已提交但审核未通过状态，4-审核通过状态', default=0)
    labs_attribute = models.ManyToManyField(LabsAttribute, verbose_name='实验室属性，用于筛选实验室，可以多个属性，也可不选')

    def __str__(self):
        return self.name
