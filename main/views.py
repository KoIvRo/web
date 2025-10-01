from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm, LoginForm, FeedbackForm

def index(request):
    latest_posts = Post.objects.all().order_by('-created_at')[:2]
    
    context = {
        'latest_posts': latest_posts,
        'now': timezone.now()
    }
    return render(request, "main/index.html", context)

def blog_list(request):
    posts = Post.objects.all()
    return render(request, "main/blog_list.html", {"posts": posts})

def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "main/blog_detail.html", {"post": post})

def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            print(f'{"FeedBack":=^30}')
            print(message)
            return redirect('home')
    else:
        form = FeedbackForm()
    return render(request, 'main/feedback.html', {'form': form})

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('home')

@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'main/add_post.html', {'form': form})

@login_required
def delete_post(request, slug):
    if not request.user.is_authenticated:
        return redirect('home')
    post = get_object_or_404(Post, slug=slug)
    post.delete()
    return redirect('blog_list')