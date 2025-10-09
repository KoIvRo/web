from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment

class FeedbackForm(forms.Form):
    mail = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Почта'}))
    message = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Сообщение'}))

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'})
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Логин'}),
        min_length=3,
        max_length=150
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Почта (опционально)'}),
        required=False
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
        min_length=4
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтверждение пароля'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].validators = []
        self.fields['password2'].validators = []
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 4:
            raise forms.ValidationError("Пароль должен содержать минимум 4 символа")
        return password1
    
class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Ваш комментарий...',
            'rows': 4,
            'style': 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;'
        })
    )
    
    class Meta:
        model = Comment
        fields = ['text']