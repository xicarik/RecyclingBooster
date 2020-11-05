from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from booster.forms import *
from booster.models import *
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import *
from django.db.models import Q

import datetime
from string import punctuation
from fastai.vision.all import *
from django.core.files.storage import FileSystemStorage

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
    return render(request, 'userpage.html', {
        'user': user,
        'news': news,
        'user_points': points(user),
        'points': points(request.user)
    })

def addpoint_page(request):
    if not request.user.is_authenticated:
        messages.add_message(request, messages.ERROR, 'Доступ к странице возможен только для авторизованных пользователй')
        return redirect('index')
    if request.method == 'POST':
        recyclespot_form = RecycleSpotForm(request.POST)
        if recyclespot_form.is_valid():
            new_recyclespot = RecycleSpot()
            new_recyclespot.geom = {'type': 'Point', 'coordinates': [
                recyclespot_form.cleaned_data.get('longitude'), recyclespot_form.cleaned_data.get('latitude')
            ]}
            new_recyclespot.point_type = recyclespot_form.cleaned_data.get('point_type')
            new_recyclespot.waste_type = recyclespot_form.cleaned_data.get('waste_type')
            new_recyclespot.adress = recyclespot_form.cleaned_data.get('adress')
            new_recyclespot.link = recyclespot_form.cleaned_data.get('link')
            new_recyclespot.save()
            messages.add_message(request, messages.SUCCESS, 'Добавлена новая точка на карте')
            return render(request, 'addpoint.html', {'form': recyclespot_form, 'points': points(request.user)})
        messages.add_message(request, messages.ERROR, 'Некорректные данные в форме')
    return render(request, 'addpoint.html', {'form': {}, 'points': points(request.user)})

def article_page(request, waste_type):
    if waste_type < 1 or waste_type > 7:
        messages.add_message(request, messages.ERROR, 'Страница не найдена')
        return redirect('index')
    article = Article.objects.filter(waste_type=waste_type)[0]
    comments = Comment.objects.filter(waste_type=waste_type)
    recyclespots = RecycleSpot.objects.filter(waste_type=waste_type)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.add_message(request, messages.ERROR, 'Публикация комментариев возможна только для авторизованных пользователй')
            return redirect('index')
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.waste_type = waste_type
            new_comment.user = request.user
            new_comment.creation_date = datetime.datetime.now()
            new_comment.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий опубликован')
            comments = Comment.objects.filter(waste_type=waste_type)
            return render(request, 'article.html', {
                'user': request.user,
                'article': article,
                'comments': comments,
                'recyclespots': recyclespots,
                'points': points(request.user),
            })
        messages.add_message(request, messages.ERROR, 'Некорректные данные в форме')
    return render(request, 'article.html', {
        'user': request.user,
        'article': article,
        'comments': comments,
        'recyclespots': recyclespots,
        'points': points(request.user),
    })

def search_page(request):
    query = request.GET.get('q')
    if query:
        for char in punctuation:
            query = query.replace(char, ' ')
        query = query.split()
        if not query:
            return render(request, 'search.html', {
                'user': request.user,
                'points': points(request.user),
            })
        patterns = Q(title__contains=query[0]) | Q(text__contains=query[0])
        for i in range(1, len(query)):
            patterns |= Q(title__contains=query[i]) | Q(text__contains=query[i])
        articles = Article.objects.filter(patterns)
        return render(request, 'search.html', {
            'user': request.user,
            'points': points(request.user),
            'query': request.GET.get('q'),
            'articles': articles,
        })
    return render(request, 'search.html', {
        'user': request.user,
        'points': points(request.user),
    })

def map_page(request, waste_type):
    collection = 0
    if waste_type < 0 or waste_type > 7:
        collection = RecycleSpot.objects.all()
    else:
        collection = RecycleSpot.objects.filter(waste_type=waste_type)
    return render(request, 'map.html', {
        'user': request.user,
        'points': points(request.user),
        'collection': collection,
    })

def recognize_page(request):
    if request.method == 'POST':
        if 'image' in request.FILES and request.FILES['image']:
            trans = [
                'Не пластик',
                '1-PET Полиэтилен',
                '2-PE-HD Полиэтилен высокой плотности',
                '3-PVC Поливинилхлорид',
                '4-PE-LD Полиэтилен низкой плотности',
                '5-PP Полипропилен',
                '6-PS Полистирол',
                '7 Другие пластики',
            ]
            learn = load_learner('booster/neuro/trained_model.pkl')
            image = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            formats = (
                '.jpg', '.JPG',
                '.JPEG', '.jpeg',
                '.png', '.PNG',
                '.GIF', '.gif',
                '.tiff', '.TIFF',
                '.bmp', '.BMP',
                '.psd', '.PSD',
            )
            alphabet = ("а","б","в","г","д","е","ё","ж","з","и","й","к","л","м","н","о",
                        "п","р","с","т","у","ф","х","ц","ч","ш","щ","ъ","ы","ь","э","ю","я")
            if any(alpha in filename for alpha in alphabet):
                messages.add_message(request, messages.ERROR, 'В названии файла не должно быть русских букв')
                return render(request, 'recognize.html', {
                    'user': request.user,
                    'points': points(request.user),
                })
            if not any(pattern in filename for pattern in formats):
                messages.add_message(request, messages.ERROR, 'Некорретный формат')
                return render(request, 'recognize.html', {
                    'user': request.user,
                    'points': points(request.user),
                })
            result = learn.predict(fs.url(filename)[1:])
            messages.add_message(request, messages.SUCCESS, f'Результат распознавания: {trans[int(result[0])]}')
            if result[0] == '0':
                return render(request, 'recognize.html', {
                    'user': request.user,
                    'points': points(request.user),
                })
            return redirect('article', waste_type=int(result[0]))
        messages.add_message(request, messages.ERROR, 'Некорректные данные в форме')
    return render(request, 'recognize.html', {
        'user': request.user,
        'points': points(request.user),
    })
