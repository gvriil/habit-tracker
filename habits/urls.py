from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    HabitViewSet,
    HabitCompletionViewSet,
    PublicHabitListView
)

router = DefaultRouter()
router.register('habits', HabitViewSet, basename='habit')
router.register('habit-completions', HabitCompletionViewSet, basename='habit-completion')

urlpatterns = [
    # Важно: этот путь должен быть ПЕРЕД include(router.urls)
    path('habit-completions/create/',
         HabitCompletionViewSet.as_view({'post': 'create'}),
         name='habit-completion-create'),

    # Остальные пути
    path('', include(router.urls)),
    path('public-habits/', PublicHabitListView.as_view(), name='public-habit-list'),
    path('my-habits/', HabitViewSet.as_view({'get': 'my_habits'}), name='my-habits'),
    path('habits/<int:pk>/complete/',
         HabitViewSet.as_view({'post': 'complete'}),
         name='habit-complete'),
    path('habits/<int:habit_id>/completions/',
         HabitCompletionViewSet.as_view({'get': 'list_by_habit'}),
         name='habit-completion-list'),
]