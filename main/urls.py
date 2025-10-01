from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('add-post/', views.add_post, name='add_post'),
    path('delete-post/<slug:slug>/', views.delete_post, name='delete_post'),
    path('feedback/', views.feedback, name='feedback'),
]