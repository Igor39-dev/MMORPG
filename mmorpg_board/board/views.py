from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.urls import reverse_lazy

from .models import Post, Reply, OneTimeCode
from .forms import PostForm

User = get_user_model()


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        if not username or not email:
            messages.error(request, "Введите имя пользователя и email")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Такой пользователь уже существует")
        else:
            user = User.objects.create_user(username=username, email=email)
            messages.success(request, "Регистрация прошла успешно. Теперь запросите код для входа.")
            return redirect("board:request_code")

    return render(request, "board/register.html")


def request_code_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден")
            return redirect("board:request_code")

        one_time_code = OneTimeCode.generate_for_user(user)
        print(f"One-time code for {user.username}: {one_time_code.code}")

        # пока просто выводим на экран (в реальном проекте — отправка на email)
        messages.success(request, f"Ваш код: {one_time_code.code}")

        return redirect("board:login_with_code")

    return render(request, "board/request_code.html")

def login_with_code_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        code = request.POST.get("code")

        try:
            user = User.objects.get(username=username)
            one_time_code = OneTimeCode.objects.filter(user=user, code=code).latest("created_at")
        except (User.DoesNotExist, OneTimeCode.DoesNotExist):
            messages.error(request, "Неверные данные")
            return redirect("board:login_with_code")

        if one_time_code.is_expired():
            messages.error(request, "Код устарел")
            return redirect("board:login_with_code")

        login(request, user)
        messages.success(request, f"Добро пожаловать, {user.username}!")
        return redirect("board:post_list")

    return render(request, "board/login_with_code.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("board:post_list")


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
    form_class = PostForm
    template_name = "board/post_form.html"
    success_url = reverse_lazy("board:post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "content", "category", "is_active"]
    template_name = "board/post_form.html"
    success_url = reverse_lazy("board:post_list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect("post_list")
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "board/post_confirm_delete.html"
    success_url = reverse_lazy("board:post_list")

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
