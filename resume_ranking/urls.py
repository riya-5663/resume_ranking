from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from resumechecker import views

urlpatterns = [
    path("admin/", admin.site.urls),

     path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('upload_resume/', views.upload_resume, name='upload_resume'),
    path('resume_score/<int:resume_id>/', views.resume_score_view, name='resume_score'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

