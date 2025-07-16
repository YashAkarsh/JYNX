from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage,name='homepage'),
    path('login/', views.loginUser,name='login'),
    path('logout/', views.logoutUser,name='logout'),
    path('signup/', views.signupUser,name='signup'),
    path('about/', views.about,name='about'),
    path('contact/', views.contact,name='contact'),
    path('terms/', views.tandc,name='tandc'),
    path('privacy/', views.privacy,name='privacypolicy'),
    path('createprofile/', views.profile_create,name='profile_creation'),



    # path('myzigs/', views.myzigs,name='myzigs'),
    # path('zig/<int:id>/', views.cmtbox),
    # path('zig/<int:id>/', views.cmtbox),
    path('share/', views.share,name='share'),
    path('settings/profile/', views.settings_ProfilePage,name='settings'),
    path('settings/account/', views.settings_Account,name='settingsAccount'),
    path('settings/myzigs/', views.settings_MyZigPage,name='settingsMyzigs'),
    path('settings/notifications/', views.settings_NotificationsPage,name='settingsNotifications'),
    # path('settingbox/', views.settingbox),
    path('robots.txt/',TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('ads.txt/',TemplateView.as_view(template_name='ads.txt', content_type='text/plain')),
    path('settings/help/', views.about,name='help'),
    path('zig/<int:id>/', views.zig,name='zig'),
    path('createzig/', views.createzig,name='createZig'),
    path('friendlist/', views.friendlist,name='friendlist'),
    # path('viewprofile/', views.viewprofile),
    path('discover/', views.discover,name='discover'),
    path('passwordreset/', views.passreset,name='resetpass'),
    path('landing/', views.landing,name='landing'),
    path('meetthedevelopers/', views.meetdevs,name='meetdevs'),
    path('email_confirmation/',views.email_confirmation,name='email_confirmation'),
    path("reset_pass/<str:code>/<str:email>", views.reset_pass_code,name="reset_pass_code"),
    path('<str:user_query>/', views.profilepage,name='profile'),

]
