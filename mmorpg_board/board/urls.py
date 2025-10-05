from django.urls import path
from . import views

app_name = "board"

urlpatterns = [
    # посты
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/add/", views.PostCreateView.as_view(), name="post_add"),
    path("post/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),

    # отклики
    path("post/<int:pk>/reply/", views.ReplyCreateView.as_view(), name="reply_add"),
    path("my-replies/", views.MyRepliesListView.as_view(), name="my_replies"),
    path("reply/<int:pk>/accept/", views.ReplyAcceptView.as_view(), name="reply_accept"),
    path("reply/<int:pk>/delete/", views.ReplyDeleteView.as_view(), name="reply_delete"),
]
