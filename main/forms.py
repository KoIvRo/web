from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Post

class FeedbackForm(forms.Form):
    mail = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Почта'}))
    message = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Сообщение'}))

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))