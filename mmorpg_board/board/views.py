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
from .forms import PostForm, RegistrationForm, CodeVerificationForm, ReplyForm


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
    template_name = "board/actions/post_detail.html"
    context_object_name = "post"

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = ReplyForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            send_mail(
                subject='На ваш пост был оставлен комментарий!',
                message=(
                    f'Привет, '
                    f'{post.user.username}!\n'
                    f'На ваше объявление "{post.title}" '
                    f'был оставлен комментарий от пользователя '
                    f'{comment.user.username} '
                    f'с содержанием:\n"{comment.content}"'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[post.user.email]
            )
            return redirect('board:post_detail', pk=post.pk)
        return render(request, 'board:post_detail.html', {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ReplyForm()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "board/actions/post_add.html"
    success_url = reverse_lazy("board:post_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "content", "category"]
    template_name = "board/actions/post_add.html"
    success_url = reverse_lazy("board:post_list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            return redirect("board:post_list")
        return super().dispatch(request, *args, **kwargs)

# -------------------------------------------------
# Отклики
# -------------------------------------------------

class MyRepliesListView(LoginRequiredMixin, ListView):
    model = Reply
    template_name = "board/my_replies.html"
    context_object_name = "user_replies"

    def get_queryset(self):
        return Reply.objects.filter(post__user=self.request.user)


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
        if obj.post.user != self.request.user:
            return redirect("board:my_replies")
        return super().dispatch(request, *args, **kwargs)


class ReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = Reply
    template_name = "board/reply_confirm_delete.html"
    success_url = reverse_lazy("board:my_replies")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post.user != self.request.user:
            return redirect("board:my_replies")
        return super().dispatch(request, *args, **kwargs)

# генерация кода / регистрация
def register_view(request):  
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if CustomUser.objects.filter(email=email, is_verified=True).exists():
                messages.error(request, "Пользователь с этим e-mail уже зарегистрирован и подтверждён.")
                return redirect('board:login')
            
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
