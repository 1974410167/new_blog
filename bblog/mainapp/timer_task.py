from .models import Post
from .views import CONN
from django.db.models import ObjectDoesNotExist

def Persistence():

    try:
        django_cache_post = CONN.hgetall("django_cache_post")

        for key in django_cache_post:

            str_key = str(key,encoding="utf-8")
            obj_pageviews = CONN.pfcount(str_key)

            try:
                obj = Post.objects.get(id=str_key)
                obj.pageviews = obj_pageviews
                obj.save()

            except ObjectDoesNotExist:
                print("Either the blog or entry doesn't exist.")

    except:
        print("django_cache_post doesn't exist.")



