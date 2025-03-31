import os
import django
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка Django для использования вне приложения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# После инициализации Django можно импортировать модели
from habits.models import Habit, HabitCompletion, TelegramProfile
from django.contrib.auth import get_user_model

# Определение состояний диалога
AUTH_STATE, HABIT_NAME, HABIT_PLACE, HABIT_ACTION, HABIT_DURATION, HABIT_TIME = range(6)

# Импорты из библиотеки python-telegram-bot
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, MessageHandler,
    Filters, ConversationHandler, CallbackQueryHandler
)

# Импорт задач Celery
from habits.tasks import schedule_reminder

User = get_user_model()

# Словарь для временного хранения данных пользователей
user_data = {}


# Команда /start - начало авторизации
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Привет! Для работы с ботом введите ваш логин и пароль через пробел.'
    )
    return AUTH_STATE


# Команда /help
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'Доступные команды:\n'
        '/start - Авторизация\n'
        '/list - Список ваших привычек\n'
        '/create - Создать новую привычку\n'
        '/complete - Отметить привычку выполненной\n'
        '/public - Просмотр публичных привычек\n'
        '/help - Помощь'
    )


# Функция авторизации
def authenticate(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.split()
    if len(user_input) != 2:
        update.message.reply_text('Пожалуйста, введите логин и пароль через пробел.')
        return AUTH_STATE

    username, password = user_input

    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            chat_id = update.effective_chat.id
            context.user_data['user_id'] = user.id
            context.user_data['username'] = user.username

            # Сохраняем chat_id в глобальный словарь для текущей сессии
            user_data[chat_id] = {
                'user_id': user.id,
                'username': user.username
            }

            # Сохраняем chat_id в базу данных для постоянного хранения
            TelegramProfile.objects.update_or_create(
                user=user,
                defaults={'chat_id': str(chat_id)}
            )

            update.message.reply_text(
                f'Вы успешно авторизованы, {user.username}!\n'
                'Используйте /help для просмотра доступных команд.'
            )
            return ConversationHandler.END
        else:
            update.message.reply_text('Неверный пароль. Попробуйте еще раз.')
            return AUTH_STATE
    except User.DoesNotExist:
        update.message.reply_text('Пользователь не найден. Попробуйте еще раз.')
        return AUTH_STATE


# Функция вывода списка привычек
def list_habits(update: Update, context: CallbackContext) -> None:
    if 'user_id' not in context.user_data:
        update.message.reply_text('Пожалуйста, авторизуйтесь с помощью команды /start')
        return

    user_id = context.user_data['user_id']
    habits = Habit.objects.filter(user_id=user_id)

    if not habits:
        update.message.reply_text(
            'У вас пока нет привычек. Создайте новую с помощью команды /create')
        return

    message = "Ваши привычки:\n"
    for i, habit in enumerate(habits, 1):
        message += f"{i}. {habit.name} - {habit.action} в {habit.place} ({habit.estimated_duration} мин)\n"

    update.message.reply_text(message)


# Начало создания привычки
def create_habit_start(update: Update, context: CallbackContext) -> int:
    if 'user_id' not in context.user_data:
        update.message.reply_text('Пожалуйста, авторизуйтесь с помощью команды /start')
        return ConversationHandler.END

    update.message.reply_text('Введите название привычки:')
    return HABIT_NAME


# Получение названия привычки
def habit_name(update: Update, context: CallbackContext) -> int:
    context.user_data['habit_name'] = update.message.text
    update.message.reply_text('Введите место выполнения привычки:')
    return HABIT_PLACE


# Получение места привычки
def habit_place(update: Update, context: CallbackContext) -> int:
    context.user_data['habit_place'] = update.message.text
    update.message.reply_text('Введите действие привычки:')
    return HABIT_ACTION


# Получение действия привычки
def habit_action(update: Update, context: CallbackContext) -> int:
    context.user_data['habit_action'] = update.message.text
    update.message.reply_text('Введите продолжительность в минутах:')
    return HABIT_DURATION


# Получение продолжительности
def habit_duration(update: Update, context: CallbackContext) -> int:
    try:
        duration = int(update.message.text)
        context.user_data['duration'] = duration
        update.message.reply_text('Введите время выполнения привычки (например, "9:00"):')
        return HABIT_TIME
    except ValueError:
        update.message.reply_text('Пожалуйста, введите число для продолжительности.')
        return HABIT_DURATION


# Добавьте этот импорт в начало файла telegram_bot.py
from habits.tasks import schedule_reminder


def habit_time(update: Update, context: CallbackContext) -> int:
    time_to_complete = update.message.text

    try:
        # Создание привычки (существующий код)
        habit = Habit.objects.create(
            user_id=context.user_data['user_id'],
            name=context.user_data['habit_name'],
            place=context.user_data['habit_place'],
            action=context.user_data['habit_action'],
            estimated_duration=context.user_data['duration'],
            is_pleasant=False,
            is_public=False,
            periodicity=1,
            time_to_complete=time_to_complete
        )

        # Планирование напоминания
        success = schedule_reminder.delay(habit.id, minutes_before=30)

        if success:
            update.message.reply_text(
                f'Привычка "{habit.name}" успешно создана! Напоминание будет отправлено за 30 минут до {time_to_complete}.'
            )
        else:
            update.message.reply_text(
                f'Привычка "{habit.name}" успешно создана! Не удалось настроить напоминания.'
            )

        return ConversationHandler.END
    except Exception as e:
        update.message.reply_text(f'Ошибка при создании привычки: {str(e)}')
        return ConversationHandler.END


# Выбор привычки для отметки о выполнении
def complete_habit(update: Update, context: CallbackContext) -> None:
    if 'user_id' not in context.user_data:
        update.message.reply_text('Пожалуйста, авторизуйтесь с помощью команды /start')
        return

    user_id = context.user_data['user_id']
    habits = Habit.objects.filter(user_id=user_id)

    if not habits:
        update.message.reply_text('У вас пока нет привычек.')
        return

    keyboard = []
    for habit in habits:
        keyboard.append([InlineKeyboardButton(habit.name, callback_data=f"complete_{habit.id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите привычку для отметки:', reply_markup=reply_markup)


# Обработка нажатия на кнопки
def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = query.data
    if data.startswith("complete_"):
        habit_id = int(data.split("_")[1])
        try:
            habit = Habit.objects.get(id=habit_id)
            HabitCompletion.objects.create(habit=habit, user_id=context.user_data.get('user_id'))
            query.edit_message_text(text=f"Привычка '{habit.name}' отмечена как выполненная!")
        except Habit.DoesNotExist:
            query.edit_message_text(text="Привычка не найдена.")


# Просмотр публичных привычек
def public_habits(update: Update, context: CallbackContext) -> None:
    if 'user_id' not in context.user_data:
        update.message.reply_text('Пожалуйста, авторизуйтесь с помощью команды /start')
        return

    public_habits = Habit.objects.filter(is_public=True)[:10]  # Ограничиваем 10 привычками

    if not public_habits:
        update.message.reply_text('Публичных привычек пока нет.')
        return

    message = "Публичные привычки:\n"
    for i, habit in enumerate(public_habits, 1):
        message += f"{i}. {habit.name} - {habit.action} в {habit.place} (автор: {habit.user.username})\n"

    update.message.reply_text(message)


def main() -> None:
    # Правильная загрузка токена из .env
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("ОШИБКА: Токен бота не найден в переменных окружения!")
        return
    print(f"Используется токен: {token[:5]}...{token[-5:]}")  # Для безопасности показываем только часть токена
    print("Запуск бота...")

    updater = Updater(token)
    dispatcher = updater.dispatcher

    # Обработчик авторизации
    auth_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AUTH_STATE: [MessageHandler(Filters.text & ~Filters.command, authenticate)],
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)],
    )

    # Отдельный обработчик создания привычек
    habit_handler = ConversationHandler(
        entry_points=[CommandHandler('create', create_habit_start)],
        states={
            HABIT_NAME: [MessageHandler(Filters.text & ~Filters.command, habit_name)],
            HABIT_PLACE: [MessageHandler(Filters.text & ~Filters.command, habit_place)],
            HABIT_ACTION: [MessageHandler(Filters.text & ~Filters.command, habit_action)],
            HABIT_DURATION: [MessageHandler(Filters.text & ~Filters.command, habit_duration)],
            HABIT_TIME: [MessageHandler(Filters.text & ~Filters.command, habit_time)],
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)],
    )

    # Регистрируем обработчики в правильном порядке
    dispatcher.add_handler(auth_handler)
    dispatcher.add_handler(habit_handler)
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("list", list_habits))
    dispatcher.add_handler(CommandHandler("complete", complete_habit))
    dispatcher.add_handler(CommandHandler("public", public_habits))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    # Запускаем бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
