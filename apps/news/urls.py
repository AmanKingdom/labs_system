from django.urls import path

from apps.news.views import NewsView, explain, NewsAPIView

app_name = 'news'

urlpatterns = [
    path('', NewsView.as_view(), name='news'),
    path('explain', explain, name='explain'),

    path('api', NewsAPIView.as_view(), name='api'),
]
