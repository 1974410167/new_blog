from django.shortcuts import render
from rest_framework.response import Response
from .serializers import PostSer
from .models import Post
from rest_framework import viewsets,mixins,generics
import time
from django_redis import get_redis_connection

CONN = get_redis_connection("default")


# /post/ 获取文章列表和创建新的文章


class PostView_List(mixins.ListModelMixin,
                    generics.GenericAPIView):

    queryset = Post.objects.all()
    serializer_class = PostSer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class PostView_Retrieve(mixins.RetrieveModelMixin,
                        generics.GenericAPIView):

    queryset = Post.objects.all()
    serializer_class = PostSer

    def get(self,request, *args, **kwargs):

        # 获得用户IP和当前的年月日小时
        remote_addr = request.META.get("REMOTE_ADDR")
        current_year = time.localtime().tm_year
        current_mon = time.localtime().tm_mon
        current_day = time.localtime().tm_mday
        current_hour = time.localtime().tm_hour

        # 拼成字符串
        redis_key_string = remote_addr+str(current_hour)+str(current_day)+str(current_mon)+str(current_year)
        

        return self.retrieve(request, *args, **kwargs)












