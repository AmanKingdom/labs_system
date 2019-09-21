from django.db import models

from apps.super_manage.models import Institute, Course, Labs, LabsAttribute, School


# 实验类型
class ExperimentType(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'experiment_type'

    name = models.CharField(max_length=30, verbose_name='实验类型')
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name='对应的学校', related_name='experiment_types')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

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
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        show_me = ''
        if self.special_consume_requirements is not "":
            show_me = show_me + '耗材:' + self.special_consume_requirements
        if self.special_system_requirements is not "":
            show_me = show_me + '系统:' + self.special_system_requirements
        if self.special_soft_requirements is not "":
            show_me = show_me + '软件:' + self.special_soft_requirements
        return show_me


# 实验项目
class Experiment(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'experiment'

    no = models.IntegerField(verbose_name='编号')
    name = models.CharField(max_length=50, verbose_name='实验项目名称')
    experiment_type = models.ForeignKey(ExperimentType, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='实验类型')
    lecture_time = models.IntegerField(verbose_name='学时')
    which_week = models.IntegerField(verbose_name='周次(哪周上课？)')
    days_of_the_week = models.IntegerField(verbose_name='星期')
    section = models.CharField(max_length=10, verbose_name='节次')
    labs = models.ManyToManyField(Labs, verbose_name='实验室')
    special_requirements = models.ForeignKey(SpecialRequirements, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='特殊需求')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='所属课程')
    status = models.IntegerField(verbose_name='状态：1-已提交但未审核，2-审核未通过，3-审核通过', default=1)
    labs_attribute = models.ManyToManyField(LabsAttribute, verbose_name='实验室属性，用于筛选实验室，可以多个属性，也可不选')

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return self.name
