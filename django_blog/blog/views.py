from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import PostForm
from .models import Post
from .forms import PostForm, CommentForm
from .models import Post, Comment
from django.db.models import Q
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from .models import Post, Tag

def post_list(request):
    posts = Post.objects.select_related('author').all()
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})



from .models import Post
from .forms import RegisterForm, UserUpdateForm, ProfileForm


# Blog views (unchanged)
def post_list(request):
    posts = Post.objects.select_related('author').all()
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


# Auth: Login/Logout provided by class-based views
class BlogLoginView(LoginView):
    template_name = 'registration/login.html'


class BlogLogoutView(LogoutView):
    template_name = 'registration/logout.html'


# Registration
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('post_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
        return render(request, 'registration/register.html', {'form': form})


# Profile view & update
@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)
        return render(request, 'registration/profile.html', {'u_form': u_form, 'p_form': p_form})
    

from .forms import PostForm
from .models import Post

class PostListView(ListView):
    model = Post
    paginate_by = 10  # optional, remove if not needed
    template_name = "blog/post_list.html"
    context_object_name = "posts"

class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class AuthorRequiredMixin(UserPassesTestMixin):
    """Allow only the author to edit/delete."""
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:post-list")

class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.object
        ctx["comments"] = post.comments.select_related("author").all()
        ctx["comment_form"] = CommentForm() if self.request.user.is_authenticated else None
        return ctx


# --- Comments ---

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment_form.html"  # not used when posting from detail, but kept for completeness

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return self.post_obj.get_absolute_url() + "#comments"


class CommentAuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class CommentUpdateView(LoginRequiredMixin, CommentAuthorRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment_form.html"

    def get_success_url(self):
        return self.object.post.get_absolute_url() + "#comments"


class CommentDeleteView(LoginRequiredMixin, CommentAuthorRequiredMixin, DeleteView):
    model = Comment
    template_name = "blog/comment_confirm_delete.html"

    def get_success_url(self):
        return self.object.post.get_absolute_url() + "#comments"


class CommentListView(ListView):
    model = Comment
    template_name = "blog/comment_list.html"
    context_object_name = "comments"

    def get_queryset(self):
        return Comment.objects.select_related("author", "post").filter(post_id=self.kwargs["post_id"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["post"] = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return ctx
    


from .forms import PostForm 
class TagPostListView(ListView):
    model = Post
    template_name = "blog/tag_post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return (
            Post.objects.filter(tags=self.tag)
            .select_related("author")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag"] = self.tag
        return ctx


class PostSearchView(ListView):
    model = Post
    template_name = "blog/post_search_results.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        if not q:
            return Post.objects.none()
        return (
            Post.objects.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(tags__name__icontains=q)
            )
            .select_related("author")
            .prefetch_related("tags")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        return ctx
class PostByTagListView(ListView):
    model = Post
    template_name = "blog/tag_post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["tag_slug"])
        return (
            Post.objects.filter(tags__in=[self.tag])
            .select_related("author")
            .prefetch_related("tags")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag"] = self.tag
        return ctx