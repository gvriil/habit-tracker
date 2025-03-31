from django.db.models import Q
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from token_management.api_client import APIClient
from .models import Habit, HabitCompletion
from .pagination import HabitPagination
from .permissions import IsPublicOrOwner
from .serializers import HabitSerializer, HabitCompletionSerializer


def get_habits_view(request):
    """
    Получение списка привычек через API-клиент.

    Возвращает список привычек пользователя в формате JSON.
    """
    client = APIClient()
    response = client.make_request(user_id=request.user.id, method="get", endpoint="/habits/")
    habits = response.json()
    return JsonResponse(habits, safe=False)


def create_habit_view(request):
    """
    Создание новой привычки через API-клиент.

    Принимает POST-запрос с данными привычки и создаёт новую привычку.
    Возвращает созданную привычку или ошибку в формате JSON.
    """
    if request.method == "POST":
        new_habit_data = {
            "name": request.POST.get("name"),
            "place": request.POST.get("place"),
            "time_to_complete": request.POST.get("time_to_complete"),
            "action": request.POST.get("action"),
            "is_pleasant": request.POST.get("is_pleasant") == "true",
            "is_public": request.POST.get("is_public") == "true",
            "periodicity": int(request.POST.get("periodicity")),
            "estimated_duration": int(request.POST.get("estimated_duration"))
        }
        client = APIClient()
        response = client.make_request(user_id=request.user.id, method="post", endpoint="/habits/",
                                       data=new_habit_data)
        return JsonResponse(response.json(), status=response.status_code)
    return JsonResponse({"error": "Invalid request method"}, status=400)


class HabitViewSet(viewsets.ModelViewSet):
    """
    API для работы с привычками.

    retrieve:
    Получение детальной информации о привычке.

    list:
    Получение всех привычек пользователя и публичных привычек.

    create:
    Создание новой привычки.

    update:
    Полное обновление привычки.

    partial_update:
    Частичное обновление привычки.

    destroy:
    Удаление привычки.
    """
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsPublicOrOwner]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_pleasant', 'is_public', 'periodicity']
    ordering_fields = ['created_at', 'name', 'periodicity']
    search_fields = ['name', 'description', 'place', 'action']

    def get_queryset(self):
        """
        Возвращает список привычек, доступных пользователю.

        Для GET-запросов возвращает собственные и публичные привычки.
        Для остальных методов возвращает только собственные привычки.
        """
        user = self.request.user
        # Для операций чтения (GET) - видит свои и публичные привычки
        if self.request.method in permissions.SAFE_METHODS:
            return Habit.objects.filter(
                Q(user=user) | Q(is_public=True)
            ).select_related('user', 'related_habit')
        # Для операций изменения - видит только свои привычки
        return Habit.objects.filter(user=user).select_related('user', 'related_habit')

    def perform_create(self, serializer):
        """
        Сохраняет текущего пользователя как владельца привычки при создании.
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Отметить привычку как выполненную.

        Создаёт запись о выполнении привычки. Доступно только владельцу привычки.
        """
        habit = self.get_object()

        # IsOwner в permission_classes уже проверяет владельца
        serializer = HabitCompletionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(habit=habit)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_habits(self, request):
        """
        Получить только свои привычки с пагинацией.

        Возвращает отфильтрованный список привычек, принадлежащих текущему пользователю.
        """
        habits = Habit.objects.filter(user=request.user).select_related('user', 'related_habit')

        # Применяем фильтры
        for backend in list(self.filter_backends):
            habits = backend().filter_queryset(request, habits, self)

        # Применяем пагинацию
        page = self.paginate_queryset(habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(habits, many=True)
        return Response(serializer.data)


class HabitCompletionViewSet(viewsets.ModelViewSet):
    """
    API для управления отметками о выполнении привычек.

    retrieve:
    Получение информации о конкретном выполнении привычки.

    list:
    Получение списка всех выполнений привычек пользователя.

    create:
    Создание новой отметки о выполнении привычки.

    update:
    Обновление информации о выполнении привычки.

    destroy:
    Удаление записи о выполнении привычки.
    """
    serializer_class = HabitCompletionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['completion_date']
    ordering_fields = ['completion_date']

    def get_queryset(self):
        """
        Возвращает список выполнений привычек текущего пользователя.
        """
        return HabitCompletion.objects.filter(
            habit__user=self.request.user
        ).select_related('habit')

    def perform_create(self, serializer):
        """
        Создаёт новую запись о выполнении привычки.

        Проверяет, что пользователь является владельцем привычки.
        """
        habit = serializer.validated_data['habit']
        if habit.user != self.request.user:
            raise permissions.PermissionDenied("Вы можете отмечать только свои привычки")
        serializer.save(user=self.request.user)  # Добавляем пользователя при сохранении

    @action(detail=False, methods=['get'])
    def list_by_habit(self, request, habit_id=None):
        """
        Получение всех отметок о выполнении для определенной привычки.

        Возвращает список всех выполнений конкретной привычки с пагинацией.
        """
        completions = self.get_queryset().filter(habit_id=habit_id)
        page = self.paginate_queryset(completions)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(completions, many=True)
        return Response(serializer.data)


class PublicHabitListView(generics.ListAPIView):
    """
    API для просмотра публичных привычек.

    Предоставляет доступ к списку всех публичных привычек с возможностью
    фильтрации, сортировки и поиска. Доступно только аутентифицированным
    пользователям.
    """
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_pleasant', 'periodicity']
    ordering_fields = ['created_at', 'name']
    search_fields = ['name', 'description', 'place', 'action']

    def get_queryset(self):
        """
        Возвращает список всех публичных привычек.
        """
        return Habit.objects.filter(is_public=True).select_related('user')