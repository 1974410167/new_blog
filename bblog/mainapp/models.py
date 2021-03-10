from django.db import models
from django.utils import timezone

# Create your models here.
# 标签

class Tag(models.Model):
    name = models.CharField("标签",max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签 '
        verbose_name_plural = verbose_name


# 分类
class Category(models.Model):
    name = models.CharField("分类",max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name


class Post(models.Model):

    # 标题和正文
    title = models.CharField("标题",max_length=30)
    body = models.TextField("正文")

    # 创建时间和修改时间
    create_time = models.DateTimeField('创建时间',default=timezone.now,db_index=True)
    modified_time = models.DateTimeField('修改时间')

    # 文章摘要
    excerpt = models.CharField('摘要',max_length=200,blank=True)

    # 分类和标签
    category = models.ForeignKey(Category,verbose_name='分类',on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag,verbose_name='标签',blank=True)

    # 浏览量
    pageviews = models.IntegerField(verbose_name="文章浏览量",default=0)


    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    # 人性化的返回值
    def __str__(self):
        return self.title

    #每一个model都有一个save方法，通过覆盖这个方法可以在model被save到数据库前指定modified_time的值为当前时间
    def save(self,*args,**kwargs):
        self.modified_time = timezone.now()
        super().save(*args,**kwargs)

class Comment(models.Model):

    name = models.CharField('名字',max_length=20)
    email = models.EmailField('邮箱',blank=True)
    text = models.TextField('内容')
    created_time = models.DateTimeField('创建时间',default=timezone.now)
    post = models.ForeignKey(Post,related_name='comments',verbose_name='文章',on_delete=models.CASCADE)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def __str__(self):
        return f'{self.name}: {self.text[:20]}'
#  文字签名
class Text_signature(models.Model):

    text = models.CharField(max_length=100)
    created_time = models.DateTimeField('创建时间',default=timezone.now)

    class Meta:
        verbose_name = '个性签名'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

class About_me(models.Model):

    text = models.TextField("关于")
    created_time = models.DateTimeField('创建时间',default=timezone.now)

    class Meta:
        verbose_name = '关于'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']