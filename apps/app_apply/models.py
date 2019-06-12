from django.db import models


# 学校
class School(models.Model):
    name = models.CharField(max_length=30, verbose_name='学校名称')

    def __str__(self):
        return self.name


# 校区
class SchoolArea(models.Model):
    name = models.CharField(max_length=30, verbose_name='校区名称')
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name='所属学校')

    def __str__(self):
        return self.name


# 学院
class Institute(models.Model):
    name = models.CharField(max_length=30, verbose_name='学院名称')
    school_area = models.ForeignKey(SchoolArea, on_delete=models.CASCADE, verbose_name='所属校区')

    def __str__(self):
        return self.name


# 班级
class Classes(models.Model):
    name = models.CharField(max_length=30, verbose_name='班级名称')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='所属学院')

    def __str__(self):
        return self.name


# 教师
class Teacher(models.Model):
    name = models.CharField(max_length=20, verbose_name='教师姓名')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='所属学院')
    account = models.IntegerField(verbose_name='登录账号，应为教师工号')
    password = models.CharField(max_length=18, verbose_name='登录密码')
    phone = models.IntegerField(verbose_name='手机号码（用于找回密码，非必填）', null=True, blank=True)

    def __str__(self):
        return self.name


# 课程
class Lesson(models.Model):
    name = models.CharField(max_length=50, verbose_name='课程名称')
    classes = models.ForeignKey(Classes, on_delete=models.CASCADE, verbose_name='授课班级')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='授课老师')

    def __str__(self):
        return self.name


# 实验类型
class ExperimentType(models.Model):
    name = models.CharField(max_length=30, verbose_name='实验类型')

    def __str__(self):
        return self.name


# 实验室
class Labs(models.Model):
    name = models.CharField(max_length=30, verbose_name='实验室名称')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='所属学院')
    number_of_people = models.IntegerField(verbose_name='容纳人数')
    dispark = models.BooleanField(verbose_name='开放情况')

    def __str__(self):
        return self.name
