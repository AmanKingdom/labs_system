import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from django.urls import reverse

from apps.news.models import News, Category

from .serializers import NewsSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination


class NewsAPIView(APIView):
    def get(self, request):
        all_news = News.objects.all()
        # 分页查询
        pg = PageNumberPagination()
        page_roles = pg.paginate_queryset(queryset=all_news, request=request, view=self)
        serializer = NewsSerializer(instance=page_roles, many=True)
        # serializer = NewsSerializer(instance=all_news, many=True)   # 全表查询
        return Response(serializer.data)

    def post(self, request):
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewsView(View):
    def get(self, request):
        category = request.GET.get('category', None)
        id = request.GET.get('id', None)
        if category:
            news = News.objects.filter(category__name=category)
        elif id:
            news = News.objects.filter(id=id)
        else:
            news = News.objects.all()

        if news:
            all_data = []
            for news_item in news:
                new_dict = {
                    'id': news_item.id,
                    'title': news_item.title,
                    'content': news_item.content,
                    'cover_img': news_item.cover_img,
                    'category': news_item.category.name,
                    'original_url': news_item.original_url,
                }
                all_data.append(new_dict)
        else:
            api_url = reverse('news:explain')
            return HttpResponse('请输入正确的参数，参数可参见<a href="' + api_url + '"></a>')
        return HttpResponse(json.dumps(all_data), content_type="application/json")


def explain(request):
    context = {
        'category': [],
        'ids': None,
    }
    all_category = Category.objects.all()
    for c in all_category:
        if c.news.all():
            context['category'].append(c)

    news = News.objects.all()
    if news:
        context['ids'] = [x.id for x in news]

    return render(request, 'news/explain.html', context)
