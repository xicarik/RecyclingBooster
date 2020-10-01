from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from booster.forms import LoginForm, RegisterForm, ContributionForm
from booster.models import Contribution
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import *

# Create your views here.

def points(user):
    if user.is_authenticated:
        return len(Contribution.objects.filter(user=user))
    return 0

def index_page(request):
    return render(request, 'index.html', {'user': request.user, 'points': points(request.user)})

def register_page(request):
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = register_form.data['username']
            password = register_form.data['password']
            repeat_password = register_form.data['repeat_password']
            if password != repeat_password:
                messages.add_message(request, messages.ERROR, 'Пароли не совпадают')
                return render(request, 'auth/register.html', {})
            if len(password) < 6 or len(password) > 30:
                messages.add_message(request, messages.ERROR, 'Пароль должен быть длиной от 6 до 30 символов')
                return render(request, 'auth/register.html', {})
            try:
                CommonPasswordValidator().validate(password)
            except:
                messages.add_message(request, messages.ERROR, 'Этот пароль слишком часто используется людьми')
                return render(request, 'auth/register.html', {})
            try:
                NumericPasswordValidator().validate(password)
            except:
                messages.add_message(request, messages.ERROR, 'Пароль должен состоять не только из цифр')
                return render(request, 'auth/register.html', {})
            try_user = authenticate(username=username, password=password)
            if try_user:
                messages.add_message(request, messages.ERROR, 'Пользователь уже существует')
                return render(request, 'auth/register.html', {})
            user = User.objects.create_user(username, password=password)
            user.save()
            login(request, user)
            messages.add_message(request, messages.SUCCESS, 'Успешная регистрация')
            return redirect('index')
        messages.add_message(request, messages.ERROR, 'Некорректные данные в форме')
        return render(request, 'auth/register.html', {})
    return render(request, 'auth/register.html', {})

def login_page(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.data['username']
            password = login_form.data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, 'Успешный вход')
                return redirect('index')
            messages.add_message(request, messages.ERROR, 'Неверный логин или пароль')
            return render(request, 'auth/login.html', {})
        messages.add_message(request, messages.ERROR, 'Некорректные данные в форме')
        return render(request, 'auth/login.html', {})
    return render(request, 'auth/login.html', {})

def logout_page(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'Успешный выход из аккаунта')
    return redirect('index')

def contribution_page(request):
    if not request.user.is_authenticated:
        messages.add_message(request, messages.ERROR, 'Доступ к странице возможен только для авторизованных пользователй')
        return redirect('index')
    if request.method == 'POST':
        contribution_form = ContributionForm(request.POST)
        if contribution_form.is_valid():
            new_contribution = contribution_form.save(commit=False)
            new_contribution.user = request.user
            new_contribution.save()
            messages.add_message(request, messages.SUCCESS, 'Получено новое вознаграждение')
            return redirect('index')
        messages.add_message(request, messages.ERROR, 'Некорректные данные в форме')
        return render(request, 'contribution.html', {'form': contribution_form, 'points': points(request.user)})
    return render(request, 'contribution.html', {'form': ContributionForm(), 'points': points(request.user)})

def mylist_page(request):
    if not request.user.is_authenticated:
        messages.add_message(request, messages.ERROR, 'Доступ к странице возможен только для авторизованных пользователй')
        return redirect('index')
    news = Contribution.objects.filter(user=request.user)
    return render(request, 'mylist.html', {'news': news, 'points': points(request.user)})

def generallist_page(request):
    news = Contribution.objects.all()
    return render(request, 'generallist.html', {'news': news, 'points': points(request.user)})

def user_page(request, user_id):
    user = User.objects.filter(id=user_id)[0]
    news = Contribution.objects.filter(user=user)
    return render(request, 'userpage.html', {\
                                            'user': user,\
                                            'news': news,\
                                            'user_points': points(user),\
                                            'points': points(request.user)})
