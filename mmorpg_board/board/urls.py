from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),

    path('reply/create/<int:post_pk>/', views.create_reply_view, name='reply_create'),

    path('register/', views.register_view, name='register'),
    path('request-code/', views.useal_login_view, name='request_code'),
    path('login-with-code/', views.login_with_code_view, name='login_with_code'),
    path('logout/', views.logout_view, name='logout'),

    path('my-replies/', views.my_replies_view, name='my_replies'),
    path('reply/<int:reply_pk>/accept/', views.accept_reply_view, name='reply_accept'),
    path('reply/<int:reply_pk>/delete/', views.delete_reply_view, name='reply_delete'),
]
