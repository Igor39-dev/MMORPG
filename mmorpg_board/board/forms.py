from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Reply, CustomUser
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = ['category', 'title', 'content']


class ReplyForm(forms.ModelForm):

    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'cols': 75}),
        }
        labels = {
            'content': '',
        }


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email, is_verified=True).exists():
            raise forms.ValidationError("Пользователь с этим e-mail уже зарегистрирован и подтверждён.")
        return email


class CodeVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'placeholder': 'Введите код'}))

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError("Код должен состоять из 6 цифр.")
        return code
