from django.contrib import admin
from .models import Habit, HabitCompletion


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'periodicity', 'created_at', 'is_active')
    list_filter = ('periodicity', 'is_active')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ('habit', 'user', 'completed_at', 'is_successful')
    list_filter = ('is_successful', 'completed_at')
    search_fields = ('habit__name', 'user__username')
    readonly_fields = ('completed_at',)