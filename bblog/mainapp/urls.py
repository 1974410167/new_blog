
from django.urls import path,include
from . import views
from rest_framework import routers


# routers = routers.SimpleRouter()
#
# routers.register(r'post',views.PostView_ListCreate,basename="PostView_ListCreate")
# routers.register(r'post/<int:pk>',views.PostView_RetrieveUpdateDestroy,basename="PostView_RetrieveUpdateDestroy")


urlpatterns = [
    # path("",include(routers.urls)),
    path('post/',views.PostView_List.as_view(),name="PostView_List"),
    path('post/<int:pk>/', views.PostView_Retrieve.as_view(), name="PostView_Retrieve"),
]