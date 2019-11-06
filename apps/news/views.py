import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from django.urls import reverse

from apps.news.models import News, Category


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
            return HttpResponse('请输入正确的参数，参数可参见<a href="'+api_url+'"></a>')
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
