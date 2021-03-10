from rest_framework import serializers
from .models import Post,Tag,Category,Comment,Text_signature,About_me

class SignSer(serializers.ModelSerializer):

    class Meta:
        model = Text_signature
        fields = ["text"]

class AboutSer(serializers.ModelSerializer):

    class Meta:
        model = About_me
        fields = ["text"]

class TagSer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["id","name",]

class PostSer(serializers.ModelSerializer):

    category = serializers.CharField(source="category.name")
    tags = TagSer(many=True,read_only=True)
    comments = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = ["id","title","body","excerpt","category","tags","create_time","modified_time","pageviews",'comments']
        depth = 1

class CategorySer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["id","name",]


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
        fields = ["id",'name','email','text','post','created_time']
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