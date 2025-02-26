from django.urls import path
from . import views

app_name = 'camera_app'

urlpatterns = [
    path('', views.index, name='index'),  # メインページのビュー
    path('video_feed/', views.video_feed, name='video_feed'),
    path('api/camera_control/', views.camera_control, name='camera_control'),
    path('api/camera_status/', views.camera_status, name='camera_status'),
]
