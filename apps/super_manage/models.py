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
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name='所属学校', related_name='school_areas')

    def __str__(self):
        return '%s-%s' % (self.school.name, self.name)


# 学院
class Institute(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'institute'

    name = models.CharField(max_length=30, verbose_name='学院名称')
    school_area = models.ForeignKey(SchoolArea, on_delete=models.CASCADE, verbose_name='所属学校与校区', related_name='institutes')

    def __str__(self):
        return '%s-%s' % (self.school_area, self.name)


# 系
class Department(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'department'

    name = models.CharField(max_length=30, verbose_name='系名称')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='所属学院', related_name='departments')

    def __str__(self):
        return '%s-%s' % (self.institute, self.name)


# 实验室属性
class LabsAttribute(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'labs_attribute'

    name = models.CharField(max_length=50, verbose_name='属性名称')
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name='对应的学校')

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
    attributes = models.ManyToManyField(LabsAttribute, verbose_name='实验室属性')

    def __str__(self):
        return self.name


# 年级
class Grade(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'grade'

    name = models.CharField(max_length=30, verbose_name='年级名称')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属系', related_name='grades')

    def __str__(self):
        return '%s-%s级' % (self.department, self.name)


# 班级
class Classes(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'classes'

    name = models.IntegerField(verbose_name='班级')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name='所属年级', related_name='classes')

    def __str__(self):
        return '%s %s班' % (self.grade, self.name)


# 教师
class Teacher(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'teacher'

    name = models.CharField(max_length=20, verbose_name='教师姓名')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属系', related_name='teachers')
    account = models.CharField(max_length=100, verbose_name='登录账号，通常为教师工号')
    password = models.CharField(max_length=18, verbose_name='登录密码', default='123456')
    phone = models.CharField(max_length=11, verbose_name='手机号码（用于找回密码，非必填）', null=True, blank=True)

    def __str__(self):
        return self.name


# 实验总体需求，包含实验教材
class TotalRequirements(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'total_requirements'

    teaching_materials = models.CharField(max_length=200, verbose_name='总体教材需求', null=True, blank=True)
    total_consume_requirements = models.CharField(max_length=100, verbose_name='总体耗材需求', null=True, blank=True)
    total_system_requirements = models.CharField(max_length=100, verbose_name='总体系统需求', null=True, blank=True)
    total_soft_requirements = models.CharField(max_length=100, verbose_name='总体软件需求', null=True, blank=True)


# 学年
class SchoolYear(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'school_year'

    since = models.IntegerField(default=2019, verbose_name='起始年份')
    to = models.IntegerField(default=2020, verbose_name='终止年份')

    def __str__(self):
        return '%s-%s学年' % (self.since, self.to)


# 学期
class Term(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'term'

    TERM = (
        ('第一学期', '第一学期'),
        ('第二学期', '第二学期'),
    )
    school_year = models.ForeignKey(SchoolYear, verbose_name='所属学年', on_delete=models.CASCADE)
    name = models.CharField(max_length=20, choices=TERM, verbose_name='学期名')
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name='对应的学校')
    begin_date = models.DateField(auto_now=True, verbose_name='当前学期起始日期')

    def __str__(self):
        return '%s%s' % (self.school_year, self.name)


# 课程
class Course(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'course'

    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='开课单位')
    name = models.CharField(max_length=50, verbose_name='课程名称')
    # 一个班级选择多个课程，一个课程可以被多个班级选择
    classes = models.ManyToManyField(Classes, verbose_name='授课班级')
    # 一个课程可以多个老师讲授，一个老师也可以讲授多个课程
    teachers = models.ManyToManyField(Teacher, verbose_name='授课老师')
    total_requirements = models.ForeignKey(TotalRequirements, on_delete=models.SET_NULL,
                                           verbose_name='总体实验需求', blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, verbose_name='学年学期')

    def __str__(self):
        return self.name


# 超级管理员
class SuperUser(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'super_user'

    name = models.CharField(max_length=20, verbose_name='超级管理员昵称')
    account = models.CharField(max_length=100, verbose_name='登录账号，用手机号码')
    password = models.CharField(max_length=18, verbose_name='登录密码', default='123456')
    school = models.ForeignKey(School, on_delete=models.SET_NULL, verbose_name='所管理的学校', blank=True, null=True)
    is_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, verbose_name='是否是教师，是则外键到对应教师', blank=True, null=True)

    def __str__(self):
        return self.name
