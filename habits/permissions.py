from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Права доступа только для владельца привычки
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsPublicOrOwner(permissions.BasePermission):
    """
    Разрешает доступ на чтение для публичных привычек,
    но редактировать может только владелец
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and obj.is_public:
            return True
        return obj.user == request.user