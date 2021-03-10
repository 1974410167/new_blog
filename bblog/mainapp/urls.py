
from django.urls import path
from . import views



urlpatterns = [

    path('post/',views.PostView_List.as_view(),name="PostView_List"),
    path('post/<int:pk>/', views.PostView_Retrieve.as_view(), name="PostView_Retrieve"),

    path('post/<int:pk>/comments/', views.Comment_RetrieveDestroy.as_view(), name="Comment_RetrieveDestroy"),
    path('post/comment/', views.Comment_Create.as_view(), name="Comment_Create"),

    path('category/', views.Category_List.as_view(), name="Category_List"),
    path('category/<int:pk>/', views.Category_Retrieve.as_view(), name="Category_Retrieve"),

    path('tag/', views.Tag_List.as_view(), name="Tag_List"),
    path('tag/<int:pk>/', views.Tag_Retrieve.as_view(), name="Tag_Retrieve"),

    path('idea/', views.Idea_List.as_view(), name="Idea_List"),
    path('rec_post/', views.RecentlyPost_List.as_view(), name="RecentlyPost_List"),

    path('show_are/', views.show_archives, name="show_archives"),

    path('sign/', views.Text_signature_List.as_view(), name="Text_signature_List"),

    path('archive/<int:year>/<int:month>/', views.Retrieve_archive.as_view(), name="Retrieve_archive"),

    path('about/', views.AboutMeList.as_view(), name="AboutMeList"),

]
