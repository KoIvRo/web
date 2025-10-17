import requests
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import PostForm, LoginForm, FeedbackForm, UserRegisterForm, CommentForm

API_URL = "http://127.0.0.1:8001"

def get_api_data(url):
    response = requests.get(f"{API_URL}{url}")
    if response.status_code == 200:
        return response.json()
    return None

def index(request):
    #latest_posts = Post.objects.all().order_by('-created_at')[:2] Раньше было так
    latest_posts = get_api_data("/articles")
    
    context = {
        'latest_posts': latest_posts,
        'now': timezone.now()
    }

    return render(request, "main/index.html", context)

def portfolio(request):
    return render(request, "main/portfolio.html")

def blog_list(request, category=None):
    message = None
    print(category)
    if category:
        valid_categories = [choice[0] for choice in Post.CATEGORY_CHOICES]
        if category not in valid_categories:
            posts = get_api_data("/articles")
            #posts = Post.objects.all()
            message = f"Категория '{category}' не найдена"
        else:
            posts = get_api_data(f"/articles/category/{category}")
            #posts = Post.objects.filter(category=category)
            message = None
    else:
        posts = get_api_data("/articles")
        #posts = Post.objects.all()

    return render(request, "main/blog_list.html", {
        "posts": posts,
        "current_category": category,
        "message": message,
        "categories": Post.CATEGORY_CHOICES
        })

def blog_detail(request, id):
    post = get_api_data(f"/articles/{id}")
    #post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            payload = {
                "text": form.cleaned_data['text'],
                "author_id": request.user.id,
                "post_id": id
            }
            resp = requests.post(f"{API_URL}/articles/{id}/comments", json=payload)
            return redirect("blog_detail", id)
    else:
        form = CommentForm()

    comments = get_api_data(f"/articles/{id}/comments")
    #comments = post.comments.all().order_by('-created_at')
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
            payload = {
                "title": form.cleaned_data['title'],
                "content": form.cleaned_data['content'],
                "category": form.cleaned_data['category'],
                "author_id": request.user.id
            }

            resp = requests.post(f"{API_URL}/articles/", json=payload)
            if resp.status_code == 201:
                return redirect('blog_list')
    else:
        form = PostForm()

    return render(request,'main/add_post.html', {"form": form})


@login_required
def delete_post(request, id):
    try:
        requests.delete(f"{API_URL}/articles/{id}")
    except:
        return redirect("home")
    
    return redirect('blog_list')

def edit_post(request):
    return render(request, 'main/edit_post')


@login_required
def edit_post(request, id):
    resp = requests.get(f"{API_URL}/articles/{id}")
    if resp.status_code == 404:
        return redirect('blog_list')
    post_data = resp.json()

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            updated_data = {
                "title": form.cleaned_data["title"],
                "content": form.cleaned_data["content"],
                "category": form.cleaned_data["category"],
            }
            put_resp = requests.put(f"{API_URL}/articles/{id}", json=updated_data)

            if put_resp.status_code == 200:
                return redirect('blog_detail', id=id)
    else:
        form = PostForm(initial={
            "title": post_data["title"],
            "content": post_data["content"],
            "category": post_data["category"],
        })

    return render(request, 'main/edit_post.html', {'form': form})


@login_required
def delete_comment(request, comment_id, post_id):
    post = get_api_data(f"/articles/{post_id}")
    comment = get_api_data(f"/comments/{comment_id}")

    if not (comment['author_id'] == request.user.id or 
            post['author_id'] == request.user.id or 
            request.user.is_staff):
        return redirect('blog_detail', id=post_id)

    resp = requests.delete(f"{API_URL}/comments/{comment_id}")
    return redirect('blog_detail', id=post_id)

@login_required
def edit_comment(request, comment_id, post_id):
    post = get_api_data(f"/articles/{post_id}")
    comment = get_api_data(f"/comments/{comment_id}")

    if not (comment['author_id'] == request.user.id or 
            post['author_id'] == request.user.id or 
            request.user.is_staff):
        return redirect('blog_detail', id=post_id)

    resp = requests.get(f"{API_URL}/comments/{comment_id}")
    if not resp:
        return redirect('blog_detail', post_id)
    
    comment_data = resp.json()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            updated_data = {
                "text": form.cleaned_data["text"],
            }
            put_resp = requests.put(f"{API_URL}/comments/{comment_id}", json=updated_data)

            if put_resp.status_code == 200:
                return redirect('blog_detail', id=post_id)
    else:
        form = CommentForm(initial={
            "text": comment_data["text"],
        })

    return render(request, 'main/edit_comment.html', {'form': form})