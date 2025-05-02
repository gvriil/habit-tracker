from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async

from telegram_bot.keyboards.keyboards import (
    get_main_keyboard,
    get_category_keyboard,
    get_frequency_keyboard,
    get_time_keyboard,
    get_back_keyboard,
)

router = Router()


class HabitStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_category = State()
    waiting_for_frequency = State()
    waiting_for_time = State()


@router.message(Command("new_habit"))
@router.message(F.text == "➕ Новая привычка")
async def create_new_habit(message: types.Message, state: FSMContext):
    """Начало создания новой привычки"""
    await state.set_state(HabitStates.waiting_for_name)
    await message.answer(
        """✏️ Создание новой привычки\n\nВведите название привычки (например, Пить воду, 
        Делать зарядку):""",
        reply_markup=get_back_keyboard(),  # Добавляем кнопку назад
    )


@router.message(HabitStates.waiting_for_name)
async def process_habit_name(message: types.Message, state: FSMContext):
    """Обработка названия привычки"""
    # Проверка на нажатие кнопки "Назад"
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
        return

    await state.update_data(habit_name=message.text)
    await state.set_state(HabitStates.waiting_for_category)
    await message.answer(
        f"Выберите категорию для привычки «{message.text}»:",
        reply_markup=get_category_keyboard(),
    )


@router.message(F.text == "⬅️ Назад")
async def back_to_main(message: types.Message, state: FSMContext):
    """Обработчик для кнопки "Назад" - возврат в главное меню"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
    await message.answer("Действие отменено", reply_markup=get_main_keyboard())
    # Отправляем приветственное сообщение главного меню
    await message.answer(
        "👋 Добро пожаловать в трекер привычек!\n\n"
        "Я помогу вам создавать и отслеживать ежедневные привычки.",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("habits"))
@router.message(F.text == "📋 Мои привычки")
async def show_habits_list(message: types.Message):
    """Показывает список привычек пользователя"""
    user_id = message.from_user.id

    # Асинхронно получаем привычки
    habits = await get_user_habits(user_id)

    if not habits:
        # Если привычек нет
        await message.answer(
            "📋 Список ваших привычек пока пуст.\n\n"
            "Создайте новую привычку с помощью кнопки ➕ Новая привычка.",
            reply_markup=get_main_keyboard(),
        )
    else:
        # Если есть привычки, выводим список
        habits_text = "📋 Ваши привычки:\n\n"
        for i, habit in enumerate(habits, 1):
            habits_text += (
                f"{i}. {habit['name']} ({habit.get('category', 'Без категории')})\n"
            )

        await message.answer(habits_text, reply_markup=get_main_keyboard())


async def get_user_habits(user_id):
    """Получение привычек пользователя"""

    @sync_to_async
    def _get_habits():
        import logging

        logger = logging.getLogger("django")

        try:
            from habits.models import Habit

            # Запрашиваем привычки из базы с фактическими полями
            habits = list(
                Habit.objects.filter(user_id=user_id).values(
                    "id",
                    "name",
                    "description",
                    "periodicity",
                    "time_to_complete",
                    "is_active",
                )
            )

            # Преобразуем данные в формат, используемый в интерфейсе бота
            for habit in habits:
                # Преобразование периодичности в текст
                period = habit.pop("periodicity", 1)
                if period == 1:
                    frequency = "Ежедневно"
                elif period == 5:
                    frequency = "По будням (Пн-Пт)"
                elif period == 2:
                    frequency = "По выходным (Сб-Вс)"
                else:
                    frequency = f"Каждые {period} дней"

                habit["category"] = habit.pop("description", "Без категории")
                habit["frequency"] = frequency
                habit["time_of_day"] = habit.pop("time_to_complete", "12:00")
                habit["active"] = habit.pop("is_active", True)

            logger.error(f"Найдено привычек: {len(habits)} для user_id={user_id}")
            return habits
        except Exception as e:
            logger.error(f"Ошибка при получении привычек: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            return []

    return await _get_habits()


@router.callback_query(HabitStates.waiting_for_category, F.data.startswith("category_"))
async def process_category(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора категории"""
    category_code = callback.data.split("_")[1]
    categories = {
        "self": "Саморазвитие",
        "sport": "Спорт",
        "health": "Здоровье",
        "study": "Учёба",
        "other": "Другое",
    }

    await state.update_data(category=categories[category_code])
    await state.set_state(HabitStates.waiting_for_frequency)

    await callback.message.edit_text(
        "Выберите частоту напоминаний:", reply_markup=get_frequency_keyboard()
    )


@router.callback_query(HabitStates.waiting_for_frequency, F.data.startswith("freq_"))
async def process_frequency(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора частоты"""
    frequency = callback.data.split("_")[1]
    frequencies = {
        "daily": "Ежедневно",
        "weekdays": "По будням (Пн-Пт)",
        "weekends": "По выходным (Сб-Вс)",
        "custom": "Выбранные дни",
    }

    await state.update_data(frequency=frequencies[frequency])
    await state.set_state(HabitStates.waiting_for_time)

    await callback.message.edit_text(
        "Выберите время для напоминания:", reply_markup=get_time_keyboard()
    )


@router.callback_query(HabitStates.waiting_for_time, F.data.startswith("time_"))
async def process_time(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора времени"""
    time_code = callback.data.split("_")[1]
    times = {
        "morning": "Утро (8:00)",
        "day": "День (13:00)",
        "evening": "Вечер (19:00)",
        "night": "Ночь (22:00)",
        "custom": "Указанное время",
    }

    time_values = {
        "morning": "08:00",
        "day": "13:00",
        "evening": "19:00",
        "night": "22:00",
        "custom": "12:00",  # значение по умолчанию для пользовательского времени
    }

    # Получаем выбранное время для отображения
    time_display = times[time_code]

    # Получаем корректное время для сохранения в БД
    time_value = time_values[time_code]

    # Получаем всю сохраненную информацию о привычке
    data = await state.get_data()
    habit_name = data.get("habit_name")
    category = data.get("category")
    frequency = data.get("frequency")

    # Очищаем состояние
    await state.clear()

    # Асинхронно сохраняем привычку в базу
    await create_habit(
        user_id=callback.from_user.id,
        name=habit_name,
        category=category,
        frequency=frequency,
        time_value=time_value,  # Передаем корректный формат времени
    )

    # Отправляем сообщение о создании привычки
    await callback.message.edit_text(
        f"✅ Привычка успешно создана!\n\n"
        f"Название: {habit_name}\n"
        f"Категория: {category}\n"
        f"Частота: {frequency}\n"
        f"Время: {time_display}\n\n"
        f"Я буду напоминать вам о необходимости выполнить эту привычку в указанное время."
    )

    # Возвращаем в главное меню
    await callback.message.answer(
        "Что хотите сделать дальше?", reply_markup=get_main_keyboard()
    )


async def create_habit(user_id, name, category, frequency, time_value):
    """Асинхронно создает привычку"""

    @sync_to_async
    def _create_habit():
        import logging

        logger = logging.getLogger("django")

        try:
            # Импорты внутри функции для работы с Django ORM
            from django.contrib.auth import get_user_model
            from habits.models import Habit

            User = get_user_model()

            # Ищем пользователя
            user = User.objects.get(id=user_id)
            logger.error(f"Пользователь найден: {user.id}")

            # Преобразуем time_value в формат времени, если нужно
            # Например, если time_value = "Утро (8:00)", выделяем "8:00"
            time_str = time_value
            if "(" in time_value and ")" in time_value:
                time_str = time_value.split("(")[1].split(")")[0]

            # Периодичность (в днях)
            period = 1  # по умолчанию ежедневно
            if frequency == "По будням (Пн-Пт)":
                period = 5  # будни
            elif frequency == "По выходным (Сб-Вс)":
                period = 2  # выходные

            # Создаем привычку с правильными полями из модели
            habit = Habit.objects.create(
                user=user,
                name=name,
                description=category,  # используем category как описание
                place="Не указано",  # значение по умолчанию
                action="Выполнить",  # значение по умолчанию
                is_active=True,
                periodicity=period,
                time_to_complete=time_str,
                estimated_duration=10,  # значение по умолчанию в минутах
                is_pleasant=False,
                is_public=False,
                reward="Личное удовлетворение",  # значение по умолчанию
            )

            logger.error(f"Привычка создана с ID: {habit.id}")
            return habit
        except Exception as e:
            logger.error(f"Ошибка при создании привычки: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    # Вызов функции
    return await _create_habit()


@router.message(Command("test_habit"))
async def test_create_habit(message: types.Message):
    """Тестовое создание привычки напрямую."""
    user_id = message.from_user.id

    await message.answer(f"Создаю тестовую привычку для пользователя {user_id}...")

    # Создаем тестовую привычку
    result = await create_habit(
        user_id=user_id,
        name="Тестовая привычка",
        category="Тест",
        frequency="Ежедневно",
        time_value="12:00",
    )

    await message.answer(f"Результат создания тестовой привычки: {result is not None}")


@router.message(Command("check_user"))
async def check_user(message: types.Message):
    """Проверка существования пользователя в Django."""

    @sync_to_async
    def _check_user():
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user_id = message.from_user.id
        exists = User.objects.filter(id=user_id).exists()
        return exists, user_id

    exists, user_id = await _check_user()
    await message.answer(f"Пользователь {user_id} существует в Django: {exists}")


@router.message(Command("debug_model"))
async def debug_habit_model(message: types.Message):
    """Показать поля модели Habit"""

    @sync_to_async
    def _get_model_info():
        from habits.models import Habit

        fields = [
            f"{field.name} ({field.__class__.__name__})"
            for field in Habit._meta.get_fields()
        ]
        return fields

    fields = await _get_model_info()
    await message.answer(f"Поля модели Habit:\n" + "\n".join(fields))
