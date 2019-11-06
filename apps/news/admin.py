from django.contrib import admin

from apps.news.models import Category, News

admin.site.register(Category)
admin.site.register(News)
