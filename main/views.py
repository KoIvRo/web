from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import PostForm, LoginForm, FeedbackForm, UserRegisterForm, CommentForm


def index(request):
    latest_posts = Post.objects.all().order_by('-created_at')[:2]
    
    context = {
        'latest_posts': latest_posts,
        'now': timezone.now()
    }
    return render(request, "main/index.html", context)

def portfolio(request):
    return render(request, "main/portfolio.html")

def blog_list(request, category=None):
    message = None
    if category:
        valid_categories = [choice[0] for choice in Post.CATEGORY_CHOICES]
        if category not in valid_categories:
            posts = Post.objects.all()
            message = f"Категория '{category}' не найдена"
        else:
            posts = Post.objects.filter(category=category)
            message = None
    else:
        posts = Post.objects.all()

    return render(request, "main/blog_list.html", {
        "posts": posts,
        "current_category": category,
        "message": message,
        "categories": Post.CATEGORY_CHOICES
        })

def blog_detail(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog_detail', id=post.id)
    else:
        form = CommentForm()

    comments = post.comments.all().order_by('-created_at')
    return render(request, "main/blog_detail.html", {"post": post, "comments": comments, "form": form})

def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            mail = form.cleaned_data['mail']
            message = form.cleaned_data['message']
            print(f'{"FeedBack":=^30}')
            print(mail)
            print(message)
            return redirect('home')
        else:
            form.clean()
    else:
        form = FeedbackForm()
    return render(request, 'main/feedback.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})

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
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'main/add_post.html', {'form': form})

@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id)

    if (not request.user.is_staff) and post.author != request.user:
        return redirect('home')
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'main/edit_post.html', {'form': form})


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        return redirect('home')
    post.delete()
    return redirect('blog_list')

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id

    if not (comment.author == request.user or 
            comment.post.author == request.user or 
            request.user.is_staff):
        return redirect('blog_detail', id=post_id)

    comment.delete()
    
    return redirect('blog_detail', id=post_id)