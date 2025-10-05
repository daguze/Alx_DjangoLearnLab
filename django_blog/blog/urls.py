from django.urls import path
from . import views


urlpatterns = [
path('', views.post_list, name='post_list'),
path('posts/<int:pk>/', views.post_detail, name='post_detail'),
path('login/', views.BlogLoginView.as_view(), name='login'),
path('logout/', views.BlogLogoutView.as_view(), name='logout'),
path('register/', views.register, name='register'),
path('profile/', views.profile, name='profile'),
]
]