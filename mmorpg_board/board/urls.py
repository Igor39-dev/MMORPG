from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "board"

urlpatterns = [
    # посты
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/add/", views.PostCreateView.as_view(), name="post_add"),

    # отклики
    path("replies/", views.RepliesView.as_view(), name="replies"),
    path('comment/<int:comment_id>/confirm/', views.confirm_comment, name='confirm_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # регистрация и одноразовый код
    path("register/", views.register_view, name="register"),
    path("login-with-code/<int:user_id>/", views.login_with_code_view, name="login_with_code"),
    path("login/", auth_views.LoginView.as_view(template_name="board/login.html"), name="login"),
    path("logout/", views.logout_view, name="logout_view"),
]
