from rest_framework.response import Response
from .serializers import PostSer,CommentSer
from .models import Post,Comment
from rest_framework import mixins, generics, status
from rest_framework.generics import RetrieveDestroyAPIView,CreateAPIView
from rest_framework.views import APIView
import time
from django_redis import get_redis_connection
# from django.views.decorators.cache import cache_page
# from django.utils.decorators import method_decorator

CONN = get_redis_connection("default")

class PostView_List(mixins.ListModelMixin,
                    generics.GenericAPIView):
    """
    获得文章列表
    """

    queryset = Post.objects.all()
    serializer_class = PostSer

    ## 增加缓存
    # @method_decorator(cache_page(60*1))
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 从redis中拿浏览量保证数据准确
        for query in queryset:
            query_pk = query.pk
            redis_pageviews_pfcount = CONN.pfcount(query_pk)
            query.pageviews = redis_pageviews_pfcount

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class PostView_Retrieve(mixins.RetrieveModelMixin,
                        generics.GenericAPIView):

        # 定制get函数,添加浏览量功能
        #
        # 具体是这样的，以文章pk为关键字，访问者的IP和当前小时数为值，建立hyperloglog。
        # 也就是说同一个用户在一个小时内点击这个文章，始终算做一次浏览量。用redis数据结构
        # hyperloglog可以极大的节约内存。

    queryset = Post.objects.all()
    serializer_class = PostSer

    def get(self,request, *args, **kwargs):
        remote_addr = request.META.get("REMOTE_ADDR")
        current_year = time.localtime().tm_year
        current_mon = time.localtime().tm_mon
        current_day = time.localtime().tm_mday
        current_hour = time.localtime().tm_hour

        redis_key_string = remote_addr+str(current_hour)+str(current_day)+str(current_mon)+str(current_year)

        pk = kwargs.get("pk")
        pk = str(pk)

        if not CONN.hexists("django_cache_post",pk):
            CONN.hset("django_cache_post",pk,1)

        CONN.pfadd(pk,redis_key_string)

        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):

        pk = kwargs.get("pk")
        pk = str(pk)

        instance = self.get_object()

        redis_post_pfcount = CONN.pfcount(pk)

        CONN.hset("django_cache_post",pk,redis_post_pfcount)
        instance.pageviews = redis_post_pfcount
        serializer = self.get_serializer(instance)

        return Response(serializer.data)


class Comment_RetrieveDestroy(RetrieveDestroyAPIView):

    queryset = Comment.objects.all()
    serializer_class = CommentSer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):

        post_pk = kwargs.get("pk")
        result = self.queryset.filter(post=post_pk)
        instance = result
        serializer = self.get_serializer(instance,many=True)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)



class Comment_Create(CreateAPIView):

    queryset = Comment.objects.all()
    serializer_class = CommentSer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # print(request.data)
        serializer = self.get_serializer(data=request.data)
        # print(serializer)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)








