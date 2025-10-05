from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from .models import Post
from django import forms
from .models import Comment
from django import forms
from .models import Post, Tag
from taggit.forms import TagWidget 

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)


    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


def save(self, commit=True):
    user = super().save(commit=False)
    user.email = self.cleaned_data["email"]
    if commit:
        user.save()
        return user


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("email",)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "avatar")


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Post title"
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": "Write your post..."
            }),
            "tags": TagWidget()
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Write your comment…"
            })
        }

    def clean_content(self):
        data = self.cleaned_data["content"].strip()
        if not data:
            raise forms.ValidationError("Comment cannot be empty.")
        return data


class PostForm(forms.ModelForm):
    tags_csv = forms.CharField(
        required=False,
        help_text="Comma-separated tags (e.g. django, python, web)."
    )

    class Meta:
        model = Post
        fields = ["title", "content", "tags_csv"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Post title"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 10, "placeholder": "Write your post..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            existing = self.instance.tags.values_list("name", flat=True)
            self.fields["tags_csv"].initial = ", ".join(existing)

    def _parse_tags(self, raw: str):
       
        parts = [t.strip() for t in (raw or "").split(",") if t.strip()]
        seen_lower = set()
        ordered = []
        for p in parts:
            key = p.lower()
            if key not in seen_lower:
                seen_lower.add(key)
                ordered.append(p)
        return ordered

    def save(self, commit=True):
        instance = super().save(commit=commit)
        tags = self._parse_tags(self.cleaned_data.get("tags_csv", ""))

        
        tag_objs = []
        for name in tags:
            obj, _ = Tag.objects.get_or_create(name=name)
            tag_objs.append(obj)

        if not instance.pk and commit:
            instance.save()

        instance.tags.set(tag_objs)
        return instance
