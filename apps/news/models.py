from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='分类名称')

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    cover_img = models.URLField(verbose_name='新闻封面图url', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name='分类', null=True, blank=True, related_name='news')
    original_url = models.URLField(verbose_name='新闻原始链接', null=True, blank=True)

    def __str__(self):
        return self.title

