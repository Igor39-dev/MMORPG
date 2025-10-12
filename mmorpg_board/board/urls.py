from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "board"

urlpatterns = [
    # посты
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/add/", views.PostCreateView.as_view(), name="post_add"),
    path("post/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_edit"),

    # отклики
    path("my-replies/", views.MyRepliesListView.as_view(), name="my_replies"),
    path("reply/<int:pk>/accept/", views.ReplyAcceptView.as_view(), name="reply_accept"),
    path("reply/<int:pk>/delete/", views.ReplyDeleteView.as_view(), name="reply_delete"),
    
    # регистрация и одноразовый код
    path("register/", views.register_view, name="register"),
    path("login-with-code/<int:user_id>/", views.login_with_code_view, name="login_with_code"),
    path("login/", auth_views.LoginView.as_view(template_name="board/login.html"), name="login"),
    path("logout/", views.logout_view, name="logout_view"),
]
