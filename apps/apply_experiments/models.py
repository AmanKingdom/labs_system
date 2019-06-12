from django.db import models


# 学校
class School(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'school'

    name = models.CharField(max_length=30, verbose_name='学校名称')

    def __str__(self):
        return self.name


# 校区
class SchoolArea(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'school_area'

    name = models.CharField(max_length=30, verbose_name='校区名称')
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name='所属学校')

    def __str__(self):
        return self.name


# 学院
class Institute(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'institute'

    name = models.CharField(max_length=30, verbose_name='学院名称')
    school_area = models.ForeignKey(SchoolArea, on_delete=models.CASCADE, verbose_name='所属校区')

    def __str__(self):
        return self.name


# 班级
class Classes(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'classes'

    name = models.CharField(max_length=30, verbose_name='班级名称')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='所属学院')

    def __str__(self):
        return self.name


# 教师
class Teacher(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'teacher'

    name = models.CharField(max_length=20, verbose_name='教师姓名')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='所属学院')
    account = models.IntegerField(verbose_name='登录账号，应为教师工号')
    password = models.CharField(max_length=18, verbose_name='登录密码')
    phone = models.IntegerField(verbose_name='手机号码（用于找回密码，非必填）', null=True, blank=True)

    def __str__(self):
        return self.name


# 课程
class Lesson(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'lesson'

    name = models.CharField(max_length=50, verbose_name='课程名称')
    classes = models.ForeignKey(Classes, on_delete=models.CASCADE, verbose_name='授课班级')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='授课老师')

    def __str__(self):
        return self.name


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
    number_of_people = models.IntegerField(verbose_name='容纳人数')
    dispark = models.BooleanField(verbose_name='开放情况')

    def __str__(self):
        return self.name


# 实验总体需求，包含实验教材
class TotalRequirements(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'total_requirements'

    total_consume_requirements = models.CharField(max_length=100, verbose_name='总体耗材需求', null=True, blank=True)
    total_system_requirements = models.CharField(max_length=100, verbose_name='总体系统需求', null=True, blank=True)
    total_soft_requirements = models.CharField(max_length=100, verbose_name='总体软件需求', null=True, blank=True)
    teaching_materials = models.CharField(max_length=200, verbose_name='总体软件需求', null=True, blank=True)


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
    total_requirements = models.ForeignKey(TotalRequirements, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='总体需求')
    special_requirements = models.ForeignKey(SpecialRequirements, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='特殊需求')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='所属课程名称')
    status = models.IntegerField(verbose_name='状态，0-草稿状态，1-已提交但未审核状态，2-已提交但审核未通过状态，4-审核通过状态')

    def __str__(self):
        return self.name


# 已有安排的实验室及其时间，时间通过实验的id从实验项目中获取
class Schedule(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'schedule'

    labs = models.CharField(max_length=20, verbose_name='实验室名称')
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, verbose_name='审核通过了的实验项目')

    def __str__(self):
        return self.labs
