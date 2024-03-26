from django.urls import path
from . import views


urlpatterns = [
    
    path('post/',views.post,name='post'),
    
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    
    path('logout/', views.logout_view, name='logout'),
    
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    
    path('forgot-pasword/',views.forgot_password,name='forgot-password'),
    
    path('change_password/', views.change_password, name='change_password'),
    
    path('login_with_otp/', views.login_with_otp, name='login_with_otp'),
    
    path('add_post/', views.add_post, name='add_post'),
    
    path('view_posts/', views.view_posts, name='view_posts'),
    
    path('view_posts/<int:post_id>/', views.view_posts, name='view_posts'),
    
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    
    
    path('translate_comment/<int:comment_id>/', views.translate_comment, name='translate_comment'), 
    
    path('mainhome/',views.Home.as_view(),name='h')
    
]