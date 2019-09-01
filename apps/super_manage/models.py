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


# 实验室属性
class LabsAttribute(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'labs_attribute'

    name = models.CharField(max_length=50, verbose_name='属性名称')
    # labs = models.ForeignKey(Labs, verbose_name='对应实验室', on_delete=models.CASCADE)

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
    attribute = models.ForeignKey(LabsAttribute, on_delete=models.SET_NULL, verbose_name='实验室属性', blank=True, null=True)

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


# 年级
class Grade(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'grade'

    name = models.CharField(max_length=30, verbose_name='年级名称')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属系')

    def __str__(self):
        return self.name


# 班级
class Classes(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'classes'

    name = models.CharField(max_length=30, verbose_name='班级名称')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name='所属年级')

    def __str__(self):
        return self.name


# 教师
class Teacher(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'teacher'

    name = models.CharField(max_length=20, verbose_name='教师姓名')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属系')
    account = models.CharField(max_length=100, verbose_name='登录账号，应为教师工号')
    password = models.CharField(max_length=18, verbose_name='登录密码', default='123456')
    phone = models.CharField(max_length=11, verbose_name='手机号码（用于找回密码，非必填）', null=True, blank=True)

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


# 课程
class Course(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'course'

    name = models.CharField(max_length=50, verbose_name='课程名称')
    # 一个班级选择多个课程，一个课程可以被多个班级选择
    classes = models.ManyToManyField(Classes, verbose_name='授课班级')
    # 一个课程可以多个老师讲授，一个老师也可以讲授多个课程
    teachers = models.ManyToManyField(Teacher, verbose_name='授课老师')
    total_requirements = models.ForeignKey(TotalRequirements, on_delete=models.CASCADE,
                                           verbose_name='总体实验需求', blank=True, null=True)

    def __str__(self):
        return self.name
