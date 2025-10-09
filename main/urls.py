from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),
    path('blog/<str:category>/', views.blog_list, name='blog_list'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('add-post/', views.add_post, name='add_post'),
    path('delete-post/<int:id>/', views.delete_post, name='delete_post'),
    path('feedback/', views.feedback, name='feedback'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('register/', views.register, name='register'),
    path('edit-post/<int:id>/', views.edit_post, name='edit_post'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]