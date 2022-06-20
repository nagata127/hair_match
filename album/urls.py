from django.urls import path
from . import views

app_name = 'album'

urlpatterns = [
    path('', views.upload, name = 'upload'),
    path('home/', views.Home.as_view(), name = 'home'),
    path('show/', views.Show_image.as_view(), name = 'show'),
    path('list/', views.IndexView.as_view(), name = 'list'),
    path('test/', views.test, name = 'test'),
]