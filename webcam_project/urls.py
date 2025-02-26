from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webcam/', include('webcam_app.urls')),  # webcam_appのURLをインクルード
    path('', include('camera_app.urls')),  # camera_appのURLをインクルード
]
