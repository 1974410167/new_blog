from django.contrib import admin
from .models import Post,Category,Tag,Comment,Text_signature,About_me


# Register your models here.
class Text_signatureAdmin(admin.ModelAdmin):

    list_display = ['text','created_time']
    fields = ['text']


class AboutMeAdmin(admin.ModelAdmin):

    list_display = ['text','created_time']
    fields = ['text']

class PostAdmin(admin.ModelAdmin):

    list_display = ['title','excerpt','create_time','category','pageviews']
    fields = ['title','body','excerpt','category','tags']

class CategoryAdmin(admin.ModelAdmin):

    list_display = ['name']
    fields = ['name']

class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    fields = ['name']

class CommentAdmin(admin.ModelAdmin):

    list_display = ['name',"email","text","post","created_time"]
    fields = ['name',"email","text","post"]


admin.site.register(Post, PostAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Tag,TagAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(Text_signature,Text_signatureAdmin)
admin.site.register(About_me,AboutMeAdmin)

