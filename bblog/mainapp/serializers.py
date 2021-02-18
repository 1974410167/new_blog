from collections import OrderedDict

from rest_framework import serializers
from .models import Comment,Post

from .models import Post,Tag,Category,Comment


class PostSer(serializers.ModelSerializer):

    category = serializers.CharField(source="category.name")
    tags = serializers.CharField(source="tags.name")

    class Meta:
        model = Post
        fields = ["title","body","excerpt","category","tags","create_time","modified_time","pageviews"]
        depth = 1


class TagSer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["name",]

class CategorySer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["name",]


class CommentSer(serializers.ModelSerializer):

    """
    重写create方法

    在post带有外键的字段时(比如Comment的post字段)，在数据库中往往是以一个ID或者
    一个字段显示，但是在django要以完整形式写入,比如
    # >>> post2 = Post.objects.filter(pk=2)
    # >>> post2
    # <QuerySet [<Post: alibb>]>
    # >>> comment_instance = Comment()
    # >>> comment_instance.name = '小李'
    # >>> comment_instance.email = 'xiao@qq.com'
    # >>> comment_instance.text = 'you are so beautiful!'
    # >>> comment_instance.post = post2[0]
    # >>> comment_instance.save()

    我们从前端postComment的时候，post字段不可能直接赋值为一个完整的post模型，只能传过来一个post的主键，
    然后后端用主键去数据库拿整条数据，赋值给Comment的Post字段
    """

    post = serializers.CharField(source='post.pk')

    class Meta:
        model = Comment
        fields = ['name','email','text','post','created_time']
        depth = 1

    def create(self, validated_data):

        post_pk = validated_data['post']['pk']
        post = Post.objects.all().get(pk=post_pk)
        comment = Comment()
        comment.name = validated_data['name']
        comment.email = validated_data['email']
        comment.text = validated_data['text']
        comment.post = post
        comment.save()

        return comment