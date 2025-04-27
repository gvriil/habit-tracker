from aiogram import Router, types, F
from telegram_bot.services import mark_habit_completed, mark_habit_skipped, get_habit_details
from telegram_bot.keyboards.keyboards import get_main_keyboard, get_habit_detail_keyboard
from telegram_bot.utils.formatters import format_streak

router = Router()


@router.callback_query(F.data.startswith("complete_"))
async def complete_habit(callback: types.CallbackQuery):
    """Обработчик нажатия кнопки "Выполнено" для привычки"""
    habit_id = int(callback.data.split("_")[1])

    # Получаем информацию о привычке перед отметкой для более информативного сообщения
    habit_info = await get_habit_details(habit_id)

    # Отмечаем привычку как выполненную
    result = await mark_habit_completed(callback.from_user.id, habit_id)

    if result.get("success"):
        streak = result.get("streak", 0)

        # Формируем базовый ответ с эмодзи и мотивацией
        response_text = f"✅ <b>Отлично! \"{habit_info['name']}\" выполнено!</b>\n\n"

        # Добавляем информацию о серии с эмодзи огня
        streak_text = format_streak(streak)
        response_text += f"🔥 <b>Текущая серия:</b> {streak_text}\n"

        # Добавляем мотивационную фразу в зависимости от длины серии
        if streak == 1:
            response_text += "\nОтличное начало! Первый шаг сделан! 💫"
        elif streak <= 3:
            response_text += "\nПродолжайте в том же духе! 💪"
        elif streak <= 7:
            response_text += "\nУже целая неделя! Вы на правильном пути! 🌟"
        elif streak <= 21:
            response_text += "\nВы формируете сильную привычку! 👑"
        else:
            response_text += "\nПотрясающе! Вы настоящий мастер дисциплины! 🏆"

        # Если есть достижение - поздравляем отдельно
        if achievement := result.get("achievement"):
            response_text += f"\n\n🏆 <b>Новое достижение!</b>\n{achievement['name']}\n{achievement['description']}"

        # Обновляем сообщение с уведомлением
        await callback.message.edit_text(response_text)

        # Отправляем дополнительное сообщение с главной клавиатурой
        await callback.message.answer("Что хотите сделать дальше?",
                                      reply_markup=get_main_keyboard())
    else:
        error_message = result.get('error', 'Неизвестная ошибка')
        await callback.message.edit_text(f"❌ Не удалось отметить выполнение: {error_message}")
        await callback.message.answer("Попробуйте еще раз позже.", reply_markup=get_main_keyboard())


@router.callback_query(F.data.startswith("skip_"))
async def skip_habit(callback: types.CallbackQuery):
    """Обработчик нажатия кнопки "Пропустить" для привычки"""
    habit_id = int(callback.data.split("_")[1])
    habit_info = await get_habit_details(habit_id)

    result = await mark_habit_skipped(callback.from_user.id, habit_id)

    if result.get("success"):
        await callback.message.edit_text(
            f"⏸ Привычка \"{habit_info['name']}\" пропущена на сегодня.\n\n"
            f"Не беспокойтесь, один пропуск не критичен. Возвращайтесь к ней завтра! 💪"
        )
        await callback.message.answer("Что хотите сделать дальше?",
                                      reply_markup=get_main_keyboard())
    else:
        error_message = result.get('error', 'Неизвестная ошибка')
        await callback.message.edit_text(f"❌ Не удалось отметить пропуск: {error_message}")
        await callback.message.answer("Попробуйте еще раз позже.", reply_markup=get_main_keyboard())


@router.callback_query(F.data.startswith("remind_"))
async def remind_later(callback: types.CallbackQuery):
    """Обработчик нажатия кнопки "Напомнить позже" для привычки"""
    habit_id = int(callback.data.split("_")[1])
    habit_info = await get_habit_details(habit_id)

    # В реальном приложении здесь должна быть логика отложенного напоминания
    await callback.message.edit_text(
        f"⏰ Я напомню вам о привычке \"{habit_info['name']}\" через 30 минут.\n\n"
        f"Уведомление придет в {callback.message.date.replace(minute=callback.message.date.minute + 30).strftime('%H:%M')}."
    )
    await callback.message.answer("Что хотите сделать дальше?", reply_markup=get_main_keyboard())


@router.callback_query(F.data.startswith("habit_"))
async def show_habit_details(callback: types.CallbackQuery):
    """Показывает детальную информацию о привычке при нажатии на неё в списке"""
    habit_id = int(callback.data.split("_")[1])
    habit_info = await get_habit_details(habit_id)

    if not habit_info:
        await callback.message.edit_text("❌ Привычка не найдена")
        return

    # Форматирование информации о привычке
    habit_text = (
        f"<b>{habit_info['name']}</b>\n\n"
        f"🗂 <b>Категория:</b> {habit_info['category']}\n"
        f"⏰ <b>Напоминание:</b> {habit_info['time']}\n"
        f"📆 <b>Частота:</b> {habit_info['frequency']}\n"
        f"🔥 <b>Текущая серия:</b> {format_streak(habit_info['streak'])}\n"
        f"📊 <b>Выполнено всего:</b> {habit_info['completions_count']} раз\n"
    )

    await callback.message.edit_text(
        habit_text,
        reply_markup=get_habit_detail_keyboard(habit_id)
    )