from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, FeedView
from django.urls import path

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('comments', CommentViewSet)


urlpatterns = [
    path('feed/', FeedView.as_view(), name='feed'),
]

urlpatterns = router.urls
