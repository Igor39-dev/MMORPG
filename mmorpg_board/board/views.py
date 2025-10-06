from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import send_mail
from django.urls import reverse_lazy

from .models import CustomUser, Post, Reply
from .forms import PostForm, RegistrationForm, CodeVerificationForm


@login_required
def logout_view(request):
    logout(request)
    return redirect("board:post_list")

# -------------------------------------------------
# Посты
# -------------------------------------------------

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
            return redirect("board:post_list")
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "board/post_confirm_delete.html"
    success_url = reverse_lazy("board:post_list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect("board:post_list")
        return super().dispatch(request, *args, **kwargs)

# -------------------------------------------------
# Отклики
# -------------------------------------------------

class ReplyCreateView(LoginRequiredMixin, CreateView):
    model = Reply
    fields = ["text"]
    template_name = "board/reply_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs["pk"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("board:post_detail", kwargs={"pk": self.kwargs["pk"]})


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
    success_url = reverse_lazy("board:my_replies")

    def form_valid(self, form):
        form.instance.is_accepted = True
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post.author != self.request.user:
            return redirect("board:my_replies")
        return super().dispatch(request, *args, **kwargs)


class ReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = Reply
    template_name = "board/reply_confirm_delete.html"
    success_url = reverse_lazy("board:my_replies")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post.author != self.request.user:
            return redirect("board:my_replies")
        return super().dispatch(request, *args, **kwargs)

# генерация кода
def register_view(request):  
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if CustomUser.objects.filter(email=email, is_verified=True).exists():
                messages.error(request, "Пользователь с этим e-mail уже зарегистрирован и подтверждён.")
                return redirect('login')
            
            user = form.save(commit=False)
            user.is_active = True
            user.is_verified = False
            user.save()

            user.generate_confirmation_token()
            send_mail(
                subject="Код подтверждения регистрации",
                message=f"Ваш код подтверждения: {user.confirmation_token}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            messages.success(request, "Регистрация успешна! На вашу почту отправлен код для подтверждения.")
            return redirect('board:login_with_code', user_id=user.id)

    else:
        form = RegistrationForm()
    return render(request, 'board/register.html', {'form': form})


def login_with_code_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = CodeVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if user.confirmation_token == code and user.is_token_valid():
                user.is_verified = True
                user.confirmation_token = None
                user.save()

                login(request, user)

                messages.success(request, "Регистрация подтверждена! Вы успешно вошли на сайт.")
                return redirect('board:post_list')
            else:
                messages.error(request, "Неверный или просроченный код.")
    else:
        form = CodeVerificationForm()
    
    return render(request, 'board/login_with_code.html', {'form': form})
