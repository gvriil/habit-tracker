from aiogram.fsm.state import State, StatesGroup

class HabitCreation(StatesGroup):
    """Состояния для создания привычки"""
    waiting_name = State()        # Ожидание ввода названия
    waiting_category = State()    # Ожидание выбора категории
    waiting_time = State()        # Ожидание выбора времени
    waiting_exact_time = State()  # Ожидание ввода точного времени (если выбрана опция)
    waiting_frequency = State()   # Ожидание выбора частоты
    waiting_days = State()        # Ожидание выбора дней недели (для частоты "выбрать дни")
    confirm_creation = State()    # Подтверждение создания привычки

class HabitEdit(StatesGroup):
    """Состояния для редактирования привычки"""
    select_field = State()        # Выбор параметра для редактирования
    edit_name = State()           # Редактирование названия
    edit_time = State()           # Редактирование времени
    edit_frequency = State()      # Редактирование частоты
    confirm_edit = State()        # Подтверждение изменений