from django.db import models


# 学校
class School(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'school'

    name = models.CharField(max_length=30, verbose_name='学校名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return self.name


# 校区
class SchoolArea(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'school_area'

    name = models.CharField(max_length=30, verbose_name='校区名称')
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name='所属学校', related_name='school_areas')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return '%s-%s' % (self.school.name, self.name)


# 学院
class Institute(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'institute'

    name = models.CharField(max_length=30, verbose_name='学院名称')
    school_area = models.ForeignKey(SchoolArea, on_delete=models.CASCADE, verbose_name='所属学校与校区',
                                    related_name='institutes')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return '%s-%s' % (self.school_area, self.name)


# 系
class Department(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'department'

    name = models.CharField(max_length=30, verbose_name='系名称')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='所属学院', related_name='departments')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return '%s-%s' % (self.institute, self.name)


# 实验室属性
class LabsAttribute(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'labs_attribute'

    name = models.CharField(max_length=50, verbose_name='属性名称')
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name='对应的学校', related_name='labs_attributes')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return self.name


# 实验室
class Lab(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'labs'

    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='所属学院', related_name='labs')
    name = models.CharField(max_length=30, verbose_name='实验室名称')
    number_of_people = models.IntegerField(verbose_name='容纳人数', default=40)
    dispark = models.BooleanField(verbose_name='开放情况', default=True)
    attributes = models.ManyToManyField(LabsAttribute, verbose_name='实验室属性')
    equipments = models.TextField(verbose_name='实验室设备信息', blank=True, null=True)
    equipments_amount = models.IntegerField(verbose_name='设备数量', default=40)

    attribute1 = models.ForeignKey(LabsAttribute, verbose_name='1号属性', blank=True, null=True, on_delete=models.SET_NULL, related_name='lab_attr1')
    attribute2 = models.ForeignKey(LabsAttribute, verbose_name='2号属性', blank=True, null=True, on_delete=models.SET_NULL, related_name='lab_attr2')
    attribute3 = models.ForeignKey(LabsAttribute, verbose_name='3号属性', blank=True, null=True, on_delete=models.SET_NULL, related_name='lab_attr3')

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return_str = '%s(%d台)' % (self.name, self.equipments_amount)
        if self.attribute1:
            return_str = return_str + ' 属性1:' + self.attribute1.name
        if self.attribute2:
            return_str = return_str + ' 属性2:' + self.attribute2.name
        if self.attribute3:
            return_str = return_str + ' 属性3:' + self.attribute3.name

        return return_str


# 年级
class Grade(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'grade'

    name = models.CharField(max_length=30, verbose_name='年级名称')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属系', related_name='grades')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return '%s-%s级' % (self.department, self.name)


# 班级
class Classes(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'classes'

    name = models.CharField(max_length=30, verbose_name='班级')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name='所属年级', related_name='classes')
    amount = models.IntegerField(verbose_name='学生人数', default=40)

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

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
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

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
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)


# 学年
class SchoolYear(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'school_year'

    since = models.IntegerField(default=2019, verbose_name='起始年份')
    to = models.IntegerField(default=2020, verbose_name='终止年份')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

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
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return '%s%s' % (self.school_year, self.name)


# 课程
class Course(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'course'

    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='开课单位', related_name='courses')
    name = models.CharField(max_length=50, verbose_name='课程名称')
    # 一个班级选择多个课程，一个课程可以被多个班级选择
    classes = models.ManyToManyField(Classes, verbose_name='授课班级')
    # 一个课程可以多个老师讲授，一个老师也可以讲授多个课程
    teachers = models.ManyToManyField(Teacher, verbose_name='授课教师')
    total_requirements = models.ForeignKey(TotalRequirements, on_delete=models.SET_NULL,
                                           verbose_name='总体实验需求', blank=True, null=True)
    attribute = models.ForeignKey(LabsAttribute, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='课程属性')

    has_block = models.BooleanField(verbose_name='是否有课程块', default=False)

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)
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
    is_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, verbose_name='是否是教师，是则外键到对应教师', blank=True,
                                   null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return self.name


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
    experiment_type = models.ForeignKey(ExperimentType, on_delete=models.SET_NULL, blank=True, null=True,
                                        verbose_name='实验类型')
    lecture_time = models.IntegerField(verbose_name='学时')
    which_week = models.IntegerField(verbose_name='周次(哪周上课？)')
    days_of_the_week = models.IntegerField(verbose_name='星期')
    section = models.CharField(max_length=10, verbose_name='节次')
    labs = models.ManyToManyField(Lab, verbose_name='实验室')
    special_requirements = models.ForeignKey(SpecialRequirements, on_delete=models.SET_NULL, null=True, blank=True,
                                             verbose_name='特殊需求')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='所属课程', related_name='experiments')
    status = models.IntegerField(verbose_name='状态：1-已提交但未审核，2-审核未通过，3-审核通过', default=1)
    labs_attribute = models.ManyToManyField(LabsAttribute, verbose_name='实验室属性，用于筛选实验室，可以多个属性，也可不选')

    aready_schedule = models.BooleanField(verbose_name='是否已经被编排', default=False)

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return self.name


# 一门课程在同一星期和同样节次、相同实验室的安排集合，暂且叫 课程块 吧
class CourseBlock(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'course_block'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')

    weeks = models.CharField(max_length=50, verbose_name='所有周次', default='')
    days_of_the_week = models.IntegerField(verbose_name='星期')
    sections = models.CharField(max_length=10, verbose_name='所有节次', default='')

    student_sum = models.IntegerField(verbose_name='课程总人数', default=0)
    experiments = models.ManyToManyField(Experiment, verbose_name='包含的实验项目', related_name='course_block')

    new_labs = models.ManyToManyField(Lab, verbose_name='新分配的实验室', related_name='course_block_for_new')
    old_labs = models.ManyToManyField(Lab, verbose_name='原来的实验室', related_name='course_block_for_old')
    same_new_old = models.BooleanField(verbose_name='分配前后实验室是否相同', default=False)

    # 目前计划：需要人工调整的课程都属于未编排
    aready_arrange = models.BooleanField(verbose_name='是否已经被编排', default=False)
    need_adjust = models.BooleanField(verbose_name='需要人工调整', default=False)
    no_change = models.BooleanField(verbose_name='不再改动', default=False)

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return '%s星期:%d节次:%s周次:%s' % (self.course.name, self.days_of_the_week, self.sections, self.weeks)


# 排课设置记录，要确保每个学院只有一个，如何设计这个单例模式？我还不懂，是使学院和主键联合约束唯一么？
class ArrangeSettings(models.Model):
    class Meta:
        # 该数据库表名自定义为如下：
        db_table = 'arrange_settings'
        unique_together = ('id', 'institute',)

    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name='设置所属学院')
    attribute1 = models.ForeignKey(LabsAttribute, on_delete=models.CASCADE, verbose_name='最优先排课属性', related_name='a1_arrange_settings')
    attribute2 = models.ForeignKey(LabsAttribute, on_delete=models.CASCADE, verbose_name='次优先排课属性', related_name='a2_arrange_settings')

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    visible = models.BooleanField(verbose_name='是否可见', default=True)

    def __str__(self):
        return '%s：最优先排课属性：%s，次优先排课属性：%s' % (self.institute.name, self.attribute1.name, self.attribute2.name)
