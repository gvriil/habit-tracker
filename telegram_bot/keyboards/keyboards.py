from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard():
    """Главная клавиатура бота"""
    buttons = [
        [
            KeyboardButton(text="📋 Мои привычки"),
            KeyboardButton(text="➕ Новая привычка"),
        ],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🏆 Достижения")],
        [KeyboardButton(text="❓ Помощь")],
    ]
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return kb


def get_habits_list_keyboard(habits):
    """Создает инлайн-клавиатуру со списком привычек пользователя"""
    buttons = []
    for habit in habits:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{habit['name']} {'🔥' if habit['streak'] > 0 else ''}",
                    callback_data=f"habit_{habit['id']}",
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text="➕ Добавить привычку", callback_data="new_habit")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_habit_detail_keyboard(habit_id):
    """Клавиатура для управления конкретной привычкой"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Отметить выполнение", callback_data=f"complete_{habit_id}"
            )
        ],
        [InlineKeyboardButton(text="📊 Статистика", callback_data=f"stats_{habit_id}")],
        [
            InlineKeyboardButton(text="📝 Изменить", callback_data=f"edit_{habit_id}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_{habit_id}"),
        ],
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data="habits_list")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_habit_notification_keyboard(habit_id):
    """Клавиатура для уведомлений о привычке"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Выполнено", callback_data=f"complete_{habit_id}"
            ),
            InlineKeyboardButton(text="⏸ Пропустить", callback_data=f"skip_{habit_id}"),
        ],
        [
            InlineKeyboardButton(
                text="⏰ Напомнить через 30 мин", callback_data=f"remind_{habit_id}"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_category_keyboard():
    """Клавиатура для выбора категории привычки"""
    buttons = [
        [
            InlineKeyboardButton(text="🧠 Саморазвитие", callback_data="category_self"),
            InlineKeyboardButton(text="💪 Спорт", callback_data="category_sport"),
        ],
        [
            InlineKeyboardButton(text="🥗 Здоровье", callback_data="category_health"),
            InlineKeyboardButton(text="📚 Учёба", callback_data="category_study"),
        ],
        [InlineKeyboardButton(text="🔄 Другое", callback_data="category_other")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_frequency_keyboard():
    """Клавиатура для выбора частоты привычки"""
    buttons = [
        [InlineKeyboardButton(text="🔄 Ежедневно", callback_data="freq_daily")],
        [
            InlineKeyboardButton(
                text="📅 По будням (Пн-Пт)", callback_data="freq_weekdays"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏖️ По выходным (Сб-Вс)", callback_data="freq_weekends"
            )
        ],
        [
            InlineKeyboardButton(
                text="📆 Выбрать дни недели", callback_data="freq_custom"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_keyboard():
    """Клавиатура для выбора времени напоминания"""
    buttons = [
        [
            InlineKeyboardButton(text="🌅 Утро (8:00)", callback_data="time_morning"),
            InlineKeyboardButton(text="☀️ День (13:00)", callback_data="time_day"),
        ],
        [
            InlineKeyboardButton(text="🌆 Вечер (19:00)", callback_data="time_evening"),
            InlineKeyboardButton(text="🌙 Ночь (22:00)", callback_data="time_night"),
        ],
        [
            InlineKeyboardButton(
                text="⏰ Указать точное время", callback_data="time_custom"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    buttons = [[KeyboardButton(text="❌ Отменить")]]
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return kb


def get_habit_action_keyboard(habit_id):
    """Клавиатура для основных действий с привычкой"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Выполнить", callback_data=f"complete_{habit_id}"
            ),
            InlineKeyboardButton(
                text="📊 Статистика", callback_data=f"stats_{habit_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔄 Редактировать", callback_data=f"edit_{habit_id}"
            ),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_{habit_id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard():
    """Клавиатура с кнопкой "Назад"""
    buttons = [[KeyboardButton(text="⬅️ Назад")]]
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return kb
