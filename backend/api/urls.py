from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_data, name='dashboard_data'),
    path('device-telemetry/', views.ingest_telemetry, name='ingest_telemetry'),
    path('login/', views.login_user, name='login_user'),
    path('register/', views.register_user, name='register_user'),
    path('download-report/', views.download_report, name='download_report'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('toggle-pump/', views.toggle_pump, name='toggle_pump'),
    path('threshold/', views.threshold_api, name='threshold_api'),
]
