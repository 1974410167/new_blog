
from django.urls import path
from . import views





urlpatterns = [
    path('post/',views.PostView_List.as_view(),name="PostView_List"),
    path('post/<int:pk>/', views.PostView_Retrieve.as_view(), name="PostView_Retrieve"),
]