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


# 系
class Department(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'department'

    name = models.CharField(max_length=30, verbose_name='系名称')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='所属学院')

    def __str__(self):
        return self.name


# 班级
class Classes(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'classes'

    name = models.CharField(max_length=30, verbose_name='班级名称')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属系')

    def __str__(self):
        return self.name


# 教师
class Teacher(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'teacher'

    name = models.CharField(max_length=20, verbose_name='教师姓名')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属系')
    account = models.IntegerField(verbose_name='登录账号，应为教师工号')
    password = models.CharField(max_length=18, verbose_name='登录密码', default='123456')
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
