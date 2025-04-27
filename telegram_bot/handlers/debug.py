from aiogram import Router, types
from aiogram.filters import Command
from asgiref.sync import sync_to_async

router = Router()

@router.message(Command("debug_model"))
async def debug_habit_model(message: types.Message):
    """Показать поля модели Habit"""

    @sync_to_async
    def _get_model_info():
        from habits.models import Habit
        fields = [f"{field.name} ({field.__class__.__name__})" for field in Habit._meta.get_fields()]
        return fields

    fields = await _get_model_info()
    await message.answer(f"Поля модели Habit:\n" + "\n".join(fields))