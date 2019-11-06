from django.urls import path

from apps.news.views import NewsView, explain

app_name = 'news'

urlpatterns = [
    path('', NewsView.as_view(), name='news'),
    path('explain', explain, name='explain'),
]
