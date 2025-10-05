
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404




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