from django.db import models
from django.utils import timezone

# Create your models here.
# 标签
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签 '
        verbose_name_plural = verbose_name


# 分类
class Category(models.Model):
    name = models.CharField(max_length=100)

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
    create_time = models.DateTimeField('创建时间',default=timezone.now)
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