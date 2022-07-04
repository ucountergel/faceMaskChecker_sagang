from . import views
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from faceMaskChecker_sagang import settings
from attendance import views

urlpatterns = [
    path('redirect-admin', RedirectView.as_view(url="/admin"),name="redirect-admin"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name="home-page"),
    path('ShowLoginPage',auth_views.LoginView.as_view(template_name="start_page.html",redirect_authenticated_user = True),name='ShowLoginPage'),
    path('superadmin', views.superadmin, name="superadmin"),
    path('admin1', views.admin1, name="admin1"),
    path('userlogin', views.login_user, name="login-user"),
    path('user-register', views.registerUser, name="register-user"),
    path('logout',views.logoutuser,name='logout'),
    path('profile',views.profile,name='profile'),
    path('prof', views.prof, name='prof'),
    path('update-profile',views.update_profile,name='update-profile'),
    path('update-profiles', views.update_profiles, name='update-profiles'),
    path('update-avatar',views.update_avatar,name='update-avatar'),
    path('update-password',views.update_password,name='update-password'),
    path('faculty',views.faculty,name='faculty-page'),
    path('manage_faculty',views.manage_faculty,name='manage-faculty-modal'),
    path(r'view_faculty/<int:pk>',views.view_faculty,name='view-faculty-modal'),
    path(r'manage_faculty/<int:pk>',views.manage_faculty,name='edit-faculty-modal'),
    path('save_faculty',views.save_faculty,name='save-faculty'),
    path('delete_faculty',views.delete_faculty,name='delete-faculty'),
    path('video_feed', views.video_feed, name='video_feed'),
    path('webcam_feed', views.webcam_feed, name='webcam_feed'),
    path('mask_feed', views.mask_feed, name='mask_feed'),
    path('mask_feeds', views.mask_feeds, name='mask_feeds'),
    path('livecam_feed', views.livecam_feed, name='livecam_feed'),
    path('lop_feed', views.livecam_feed, name='SocialDistanceAnalysis'),

]
