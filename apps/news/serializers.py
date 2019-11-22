from rest_framework import serializers
from .models import News

# 设置下拉内容
# news_id = News.objects.values('id').all()
# print(news_id)
# TYPE_CHOICES = [item['id'] for item in news_id]


# class MySerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     title = serializers.CharField(required=True, allow_blank=False, max_length=200)
#     content = serializers.CharField(max_length=10000)
#     cover_img = serializers.URLField(max_length=300)
#     category = serializers.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name='分类', null=True, blank=True,
#                                  related_name='news')
#     original_url = serializers.URLField(verbose_name='新闻原始链接', null=True, blank=True)


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'
