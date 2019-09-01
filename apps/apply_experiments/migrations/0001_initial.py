# Generated by Django 2.1 on 2019-06-20 04:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('super_manage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='实验项目名称')),
                ('lecture_time', models.IntegerField(verbose_name='学时')),
                ('which_week', models.IntegerField(verbose_name='周次(哪周上课？)')),
                ('days_of_the_week', models.IntegerField(verbose_name='星期')),
                ('section', models.IntegerField(verbose_name='节次')),
                ('status', models.IntegerField(default=0, verbose_name='状态，0-草稿状态，1-已提交但未审核状态，2-已提交但审核未通过状态，4-审核通过状态')),
            ],
            options={
                'db_table': 'experiment',
            },
        ),
        migrations.CreateModel(
            name='ExperimentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='实验类型')),
            ],
            options={
                'db_table': 'experiment_type',
            },
        ),
        migrations.CreateModel(
            name='SpecialRequirements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('special_consume_requirements', models.CharField(blank=True, max_length=100, null=True, verbose_name='特殊耗材需求')),
                ('special_system_requirements', models.CharField(blank=True, max_length=100, null=True, verbose_name='特殊系统需求')),
                ('special_soft_requirements', models.CharField(blank=True, max_length=100, null=True, verbose_name='特殊软件需求')),
            ],
            options={
                'db_table': 'special_requirements',
            },
        ),
        migrations.AddField(
            model_name='experiment',
            name='experiment_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apply_experiments.ExperimentType', verbose_name='实验类型'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='labs',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='super_manage.Labs', verbose_name='实验室'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='labs_attribute',
            field=models.ManyToManyField(blank=True, null=True, to='super_manage.LabsAttribute', verbose_name='实验室属性，用于筛选实验室，可以多个属性，也可不选'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='super_manage.Course', verbose_name='所属课程名称'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='special_requirements',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apply_experiments.SpecialRequirements', verbose_name='特殊需求'),
        ),
    ]
