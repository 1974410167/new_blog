from rest_framework.response import Response
from .serializers import PostSer
from .models import Post
from rest_framework import mixins,generics
import time
from django_redis import get_redis_connection
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

CONN = get_redis_connection("default")

class PostView_List(mixins.ListModelMixin,
                    generics.GenericAPIView):

    queryset = Post.objects.all()
    serializer_class = PostSer

    @method_decorator(cache_page(60*15))
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class PostView_Retrieve(mixins.RetrieveModelMixin,
                        generics.GenericAPIView):

    # 定制get函数,添加浏览量功能

    # 具体是这样的，以文章pk为关键字，访问者的IP和当前小时数为值，建立hyperloglog。
    # 也就是说同一个用户在一个小时内点击这个文章，始终算做一次浏览量。用redis数据结构
    # hyperloglog可以极大的节约内存。

    queryset = Post.objects.all()
    serializer_class = PostSer

    @method_decorator(cache_page(60*15))
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

        post_pfcount = CONN.pfcount(pk)
        instance.pageviews = post_pfcount
        CONN.hset("django_cache_post",pk,post_pfcount)

        serializer = self.get_serializer(instance)

        return Response(serializer.data)














