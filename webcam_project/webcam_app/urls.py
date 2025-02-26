from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cameras/', views.camera_list, name='camera_list'),
    path('camera/<int:camera_id>/stream/', views.camera_stream, name='camera_stream'),
]