from rest_framework.response import Response
from .serializers import PostSer,CommentSer,CategorySer,TagSer,SignSer,AboutSer
from .models import Post,Comment,Category,Tag,Text_signature,About_me
from rest_framework import mixins, generics, status
from rest_framework.generics import RetrieveDestroyAPIView,CreateAPIView,ListAPIView,RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
import time
from django_redis import get_redis_connection
from django.db.models import ObjectDoesNotExist
# from django.views.decorators.cache import cache_page
# from django.utils.decorators import method_decorator
from django.http import JsonResponse

CONN = get_redis_connection("default")

### 从redis中同步浏览量
def sync_pageviews(queryset):

    for query in queryset:
        query_pk = query.pk
        redis_pageviews_pfcount = CONN.pfcount(query_pk)
        query.pageviews = redis_pageviews_pfcount

### 分页
class post_SetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 10000

## 全部文章
class PostView_List(mixins.ListModelMixin,
                    generics.GenericAPIView):
    """
    获得文章列表
    """

    queryset = Post.objects.all()
    serializer_class = PostSer
    pagination_class = post_SetPagination

    ## 增加缓存
    # @method_decorator(cache_page(60*1))
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 从redis中拿浏览量保证数据准确
        sync_pageviews(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


### 检索单个文章
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


### 检索与删除评论
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

### 添加评论
class Comment_Create(CreateAPIView):

    queryset = Comment.objects.all()
    serializer_class = CommentSer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


### 全部分类
class Category_List(ListAPIView):

    queryset = Category.objects.all()
    serializer_class = CategorySer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        dict_t = {}
        post_all = Post.objects.all()

        for Cate in queryset:
            cate_id = Cate.id
            t = post_all.filter(category=cate_id)
            l = len(t)
            dict_t[cate_id] = l

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        result = serializer.data

        for item_dict in result:
            id = item_dict['id']
            post_num = dict_t.get(id)
            item_dict['num_cate'] = post_num

        return Response(result)


### 检索单个分类下的所有文章
class Category_Retrieve(RetrieveAPIView):

    queryset = Post.objects.all()
    serializer_class = PostSer

    def retrieve(self, request, *args, **kwargs):

        category_pk = kwargs.get("pk")
        result = self.queryset.filter(category=category_pk)

        sync_pageviews(result)

        instance = result
        serializer = self.get_serializer(instance,many=True)
        return Response(serializer.data)

### 全部标签
class Tag_List(ListAPIView):

    queryset = Tag.objects.all()
    serializer_class = TagSer

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        dict_t = {}
        post_all = Post.objects.all()

        for Cate in queryset:

            cate_id = Cate.id
            t = post_all.filter(tags=cate_id)
            l = len(t)
            dict_t[cate_id] = l

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        result = serializer.data

        for item_dict in result:
            id = item_dict['id']
            post_num = dict_t.get(id)
            item_dict['num_tag'] = post_num

        return Response(result)


#### 检索单个标签下的所有文章
class Tag_Retrieve(RetrieveAPIView):

    queryset = Post.objects.all()
    serializer_class = PostSer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):

        tag_pk = kwargs.get("pk")
        result = self.queryset.filter(tags=tag_pk)

        sync_pageviews(result)

        instance = result
        serializer = self.get_serializer(instance,many=True)
        return Response(serializer.data)


### 想法，返回所有分类为“想法”的文章
class Idea_List(ListAPIView):

    queryset = Post.objects.all()
    serializer_class = PostSer

    def list(self, request, *args, **kwargs):

        global idea_id
        try:
            idea_obj = Category.objects.filter(name="想法")
            idea_id = idea_obj[0].pk
        except:
            t = Category()
            t.name = "想法"
            t.save()
            queryset = {'message':'想法不存在，已创建'}
            return Response(queryset)

        queryset = self.queryset.filter(category=idea_id)

        sync_pageviews(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


### 检索最近的五篇文章

class RecentlyPost_List(mixins.ListModelMixin,
                    generics.GenericAPIView):
    """
    获得文章列表
    """

    queryset = Post.objects.all()
    serializer_class = PostSer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        if len(queryset)>5:
            queryset = queryset[:5]

        # 从redis中拿浏览量保证数据准确
        sync_pageviews(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

def show_archives(request):

    date_list=Post.objects.dates('create_time', 'month', order='DESC')

    data = []
    status_code = None
    message = ''

    result = {
        "status_code":status_code,
        "message":message,
        "data":data
    }

    if not result:
        status_code = 200
        message = "此时数据库为空"
        return result

    id = 0
    for query in date_list:
        t = {}
        t["id"] = id
        t["year"] = query.year
        t["month"] = query.month
        data.append(t)
        id += 1
    status_code = 200
    return JsonResponse(result)

class Text_signature_List(mixins.ListModelMixin,
                    generics.GenericAPIView):
    """
    获得文章列表
    """

    queryset = Text_signature.objects.all()
    serializer_class = SignSer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if len(queryset)>1:
            queryset = [queryset[0]]

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AboutMeList(mixins.ListModelMixin,
                    generics.GenericAPIView):
    """
    获得文章列表
    """

    queryset = About_me.objects.all()
    serializer_class = AboutSer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if len(queryset)>1:
            queryset = [queryset[0]]

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class Retrieve_archive(ListAPIView):

    queryset = Post.objects.all()
    serializer_class = PostSer

    def list(self, request, *args, **kwargs):

        year = kwargs.get("year")
        month = kwargs.get("month")

        queryset = self.queryset.filter(create_time__month=month,
                                        create_time__year=year
                                        ).order_by('-create_time')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)