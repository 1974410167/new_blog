from rest_framework import serializers
from .models import Post,Tag,Category


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