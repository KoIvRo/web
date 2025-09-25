from django.shortcuts import render, get_object_or_404
from .models import Post

def index(request):
    latest_posts = Post.objects.all().order_by('-created_at')[:2]
    
    context = {
        'latest_posts': latest_posts
    }
    return render(request, "main/index.html", context)

def blog_list(request):
    posts = Post.objects.all()
    return render(request, "main/blog_list.html", {"posts": posts})

def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "main/blog_detail.html", {"post": post})