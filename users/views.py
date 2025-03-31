from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User
from .serializers import UserSerializer, UserUpdateSerializer
from rest_framework.authtoken.models import Token


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Обычные пользователи видят только свой профиль, админы - всех
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить данные текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def connect_telegram(self, request):
        """Привязать Telegram аккаунт."""
        user = request.user
        telegram_id = request.data.get('telegram_id')
        telegram_username = request.data.get('telegram_username')

        if not telegram_id:
            return Response(
                {"error": "Telegram ID обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.telegram_id = telegram_id
        user.telegram_username = telegram_username
        user.telegram_notifications = True
        user.save()

        return Response({"status": "Telegram подключен успешно"})


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": serializer.data,
            "token": token.key
        })