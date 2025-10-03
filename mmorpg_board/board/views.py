from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .models import Post, Reply
from .forms import PostForm

class PostListView(ListView):
    model = Post
    template_name = "board/post_list.html"
    context_object_name = "posts"
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = "board/post_detail.html"
    context_object_name = "post"


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "content", "category"]
    template_name = "board/post_form.html"
    success_url = reverse_lazy("post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "content", "category", "is_active"]
    template_name = "board/post_form.html"
    success_url = reverse_lazy("post_list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect("post_list")
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "board/post_confirm_delete.html"
    success_url = reverse_lazy("post_list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect("post_list")
        return super().dispatch(request, *args, **kwargs)


class ReplyCreateView(LoginRequiredMixin, CreateView):
    model = Reply
    fields = ["text"]
    template_name = "board/reply_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs["pk"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"pk": self.kwargs["pk"]})


class MyRepliesListView(LoginRequiredMixin, ListView):
    model = Reply
    template_name = "board/my_replies.html"
    context_object_name = "replies"

    def get_queryset(self):
        return Reply.objects.filter(post__author=self.request.user)


class ReplyAcceptView(LoginRequiredMixin, UpdateView):
    model = Reply
    fields = []
    template_name = "board/reply_accept.html"
    success_url = reverse_lazy("my_replies")

    def form_valid(self, form):
        form.instance.is_accepted = True
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post.author != self.request.user:
            return redirect("my_replies")
        return super().dispatch(request, *args, **kwargs)


class ReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = Reply
    template_name = "board/reply_confirm_delete.html"
    success_url = reverse_lazy("my_replies")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post.author != self.request.user:
            return redirect("my_replies")
        return super().dispatch(request, *args, **kwargs)
