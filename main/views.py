import requests
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm, LoginForm, FeedbackForm, UserRegisterForm, CommentForm
from .auth import create_access_token, create_refresh_token, refresh_access_token

API_URL = "http://127.0.0.1:8001"

"""
Я ХРАНЮ ТОКЕНЫ В КУКАХ САЙТА ДЖАНГО
К API Я ХОЖУ ИСПОЛЬЗУЯ ЭТИ ТОКЕНЫ И ПОДСТАВЛЯЮ ИХ В ЗАГОЛОВКИ
ЛОГИКА СОЗДАНИЯ И ВОССТАНОВЛЕНИЯ ТОКЕНОВ В ДЖАНГО auth.py
ЛОГИКА ПРОВЕРКИ ТОКЕНОВ В API auth.py
"""


"""
НАДО В МЕТОДАХ С МЕТКОЙ ДОДЕЛАТЬ ДОБАВИТЬ ТОКЕНЫ В ЗАГОДВОКИ ДЛЯ ОТПРАВКИ НА API
"""

def get_api_data(url, request):
    headers = {}
    access, refresh = None, None
    if request:
        access = request.COOKIES.get("access_token")
        refresh = request.COOKIES.get("refresh_token")

    if not access and refresh:
        access = refresh_access_token(refresh)

    # Взял куки подставил в заголовок
    if access:
        headers["Authorization"] = f"Bearer {access}"

    try:
        response = requests.get(f"{API_URL}{url}", headers=headers)
        print(response.status_code, access)
        # Если исключение не пробросилось, значит access токен не валиден и api активен
        if response.status_code == 200:
            return response.json()
        if response.status_code != 200 and access:
            response = HttpResponseRedirect(request.path_info)
            response.set_cookie("access_token", access, httponly=True, samesite="Lax", max_age=60*15)
            return response
        else:
            return None
    except:
        # Исключение когда отказ соединения
        return None


def index(request):
    latest_posts = get_api_data("/articles/", request)
    context = {
        'now': timezone.now()
    }

    # Если вернется редирект его надо сразу обраотать что бы поставить куки
    if isinstance(latest_posts, HttpResponseRedirect):
        return latest_posts
    

    if latest_posts:
        context['latest_posts'] = latest_posts[:2]

    return render(request, "main/index.html", context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            access = create_access_token(user.id)
            refresh = create_refresh_token(user.id)
            request.session["access_token"] = access
            request.session["refresh_token"] = refresh

            response = redirect("home")
            response.set_cookie(
                "access_token",
                access,
                httponly=True,
                samesite="Lax",
                max_age=60*15
            )
            response.set_cookie(
                "refresh_token",
                refresh,
                httponly=True,
                samesite="Lax",
                max_age=60*60*24*7
            )

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
            user = form.get_user()
            login(request, user)

            access = create_access_token(user.id)
            refresh = create_refresh_token(user.id)
            request.session["access_token"] = access
            request.session["refresh_token"] = refresh

            response = redirect('home')
            response.set_cookie(
                "access_token",
                access,
                httponly=True, # Защита от XSS JS не может получить данные из этого заголовка
                secure=False, # Передача только по HTTPS, если True
                samesite="Lax", # Отправка куи при переходе по ссылкам
                max_age=60*15
            )
            response.set_cookie(
                "refresh_token",
                refresh,
                httponly=True,
                samesite="Lax",
                max_age=60*60*24*7
            )

            return response
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})


def custom_logout(request):
    response = redirect("home")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    logout(request)
    return response

def portfolio(request):
    return render(request, "main/portfolio.html")

def blog_list(request, category=None):
    message = None
    if category:
        valid_categories = [choice[0] for choice in Post.CATEGORY_CHOICES]
        if category not in valid_categories:
            posts = get_api_data("/articles", request)
            message = f"Категория '{category}' не найдена"
        else:
            posts = get_api_data(f"/articles/category/{category}", request)
            message = None
    else:
        posts = get_api_data("/articles", request)

    return render(request, "main/blog_list.html", {
        "posts": posts,
        "current_category": category,
        "message": message,
        "categories": Post.CATEGORY_CHOICES
        })


# Доделать POST запрос с jwt
def blog_detail(request, id):
    post = get_api_data(f"/articles/{id}", request)
    if not post:
        return redirect('blog_list')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            payload = {
                "text": form.cleaned_data['text'],
                "author_id": request.user.id,
                "post_id": id
            }
            try:
                resp = requests.post(f"{API_URL}/comments", json=payload)
            except:
                return redirect("blog_detail", id)
            return redirect("blog_detail", id)
    else:
        form = CommentForm()

    comments = get_api_data(f"/articles/{id}/comments", request)
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

# Доделать POST с jwt
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
            try:
                resp = requests.post(f"{API_URL}/articles/", json=payload)
            except:
                return redirect('blog_list')
            if resp.status_code == 201:
                return redirect('blog_list')
    else:
        form = PostForm()

    return render(request,'main/add_post.html', {"form": form})

# Доделать
@login_required
def delete_post(request, id):
    try:
        requests.delete(f"{API_URL}/articles/{id}")
    except:
        return redirect("home")
    
    return redirect('blog_list')

# Доделать
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
            try:
                put_resp = requests.put(f"{API_URL}/articles/{id}", json=updated_data)
            except:
                return redirect('blog_detail', id=id)
            if put_resp.status_code == 200:
                return redirect('blog_detail', id=id)
    else:
        form = PostForm(initial={
            "title": post_data["title"],
            "content": post_data["content"],
            "category": post_data["category"],
        })

    return render(request, 'main/edit_post.html', {'form': form})

# Доделать
@login_required
def delete_comment(request, comment_id, post_id):
    post = get_api_data(f"/articles/{post_id}")
    comment = get_api_data(f"/comments/{comment_id}")

    if not (comment['author_id'] == request.user.id or 
            post['author_id'] == request.user.id or 
            request.user.is_staff):
        return redirect('blog_detail', id=post_id)

    try:
        resp = requests.delete(f"{API_URL}/comments/{comment_id}")
    except:
        return redirect('blog_detail', id=post_id)
    return redirect('blog_detail', id=post_id)

# Доделать
@login_required
def edit_comment(request, comment_id, post_id):
    post = get_api_data(f"/articles/{post_id}")
    comment = get_api_data(f"/comments/{comment_id}")

    if not (comment['author_id'] == request.user.id or 
            post['author_id'] == request.user.id or 
            request.user.is_staff):
        return redirect('blog_detail', id=post_id)

    try:
        resp = requests.get(f"{API_URL}/comments/{comment_id}")
    except:
        return redirect('blog_detail', post_id)
    if not resp:
        return redirect('blog_detail', post_id)
    
    comment_data = resp.json()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            updated_data = {
                "text": form.cleaned_data["text"],
            }
            try:
                put_resp = requests.put(f"{API_URL}/comments/{comment_id}", json=updated_data)
            except:
                return redirect('blod_detail', id=post_id)
            if put_resp.status_code == 200:
                return redirect('blog_detail', id=post_id)
    else:
        form = CommentForm(initial={
            "text": comment_data["text"],
        })

    return render(request, 'main/edit_comment.html', {'form': form})