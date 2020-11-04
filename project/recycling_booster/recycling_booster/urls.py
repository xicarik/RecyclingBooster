"""recycling_booster URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from booster import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index_page, name='index'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),
    path('contribution/', views.contribution_page, name='contribution'),
    path('mylist/', views.mylist_page, name='mylist'),
    path('generallist/', views.generallist_page, name='generallist'),
    path('user/<int:user_id>/', views.user_page, name='userpage'),
    path('addpoint/', views.addpoint_page, name='addpoint'),
    path('article/<int:waste_type>/', views.article_page, name='article'),
    path('search/', views.search_page, name='search'),
    path('map/<int:waste_type>/', views.map_page, name='map'),
    path('recognize/', views.recognize_page, name='recognize'),
]
