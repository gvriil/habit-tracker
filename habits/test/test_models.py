from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from habits.models import Habit, HabitCompletion
from habits.validators import validate_related_habit, validate_reward, validate_duration, \
    validate_periodicity

User = get_user_model()


class HabitModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создание пользователя для тестов
        cls.user = User.objects.create_user(username='testuser', password='12345')

        # Создание привычки
        cls.habit = Habit.objects.create(
            user=cls.user,
            name='Тестовая привычка',
            place='Дом',
            action='Делать отжимания',
            is_pleasant=False,
            periodicity=1,
            estimated_duration=2,
            is_public=True,
            time_to_complete='09:00'
        )

    def test_habit_creation(self):
        """Тест создания привычки"""
        self.assertEqual(str(self.habit), 'Тестовая привычка (testuser)')

    def test_habit_str_method(self):
        """Тест строкового представления привычки"""
        self.assertEqual(str(self.habit), f'Тестовая привычка (testuser)')

    def test_duration_validator(self):
        """Тест валидатора продолжительности"""
        with self.assertRaises(ValidationError):
            validate_duration(121)  # Должно вызвать ошибку, т.к. > 120

        # Проверяем, что значения в пределах нормы не вызывают ошибок
        try:
            validate_duration(1)
            validate_duration(120)
        except ValidationError:
            self.fail("validate_duration вызвал ValidationError для допустимого значения")

    def test_related_habit_validator(self):
        """Тест валидатора связанных привычек"""
        pleasant_habit = Habit.objects.create(
            user=self.user,
            name='Приятная привычка',
            place='Дом',
            action='Слушать музыку',
            is_pleasant=True,
            periodicity=1,
            estimated_duration=5,
            time_to_complete='10:00'
        )

        non_pleasant_habit = Habit.objects.create(
            user=self.user,
            name='Неприятная привычка',
            place='Дом',
            action='Мыть посуду',
            is_pleasant=False,
            periodicity=1,
            estimated_duration=5,
            time_to_complete='10:00'
        )

        # Проверка валидации связанной привычки
        try:
            validate_related_habit(pleasant_habit, None)
        except ValidationError:
            self.fail("validate_related_habit вызвал ошибку для приятной привычки без награды")

        # Нельзя связать с неприятной привычкой
        with self.assertRaises(ValidationError):
            validate_related_habit(non_pleasant_habit, None)

    def test_reward_validator(self):
        """Тест валидатора награды"""
        # Проверка на наличие и связанной привычки, и награды одновременно
        pleasant_habit = Habit.objects.create(
            user=self.user,
            name='Приятная привычка',
            place='Дом',
            action='Смотреть сериал',
            is_pleasant=True,
            periodicity=1,
            estimated_duration=5,
            time_to_complete='10:00'
        )

        with self.assertRaises(ValidationError):
            validate_reward("Награда", pleasant_habit)

        # Проверка допустимых комбинаций
        try:
            validate_reward("Награда", None)
            validate_reward(None, pleasant_habit)
            validate_reward(None, None)
        except ValidationError:
            self.fail("validate_reward вызвал ошибку для допустимых комбинаций")

    def test_default_values(self):
        """Тест значений по умолчанию"""
        habit = Habit.objects.create(
            user=self.user,
            name='Минимальная привычка',
            place='Дом',
            action='Делать минимум',
            time_to_complete='12:00'
        )
        self.assertFalse(habit.is_pleasant)
        self.assertEqual(habit.periodicity, 1)  # По умолчанию 1 день
        self.assertFalse(habit.is_public)

    def test_habit_fields_validation(self):
        """Тест валидации полей привычки"""
        # Проверим другие поля, которые точно должны проходить валидацию
        habit = Habit(
            user=self.user,
            name='Валидная привычка',
            place='Дом',
            action='Тест',
            time_to_complete='10:00'
        )
        try:
            habit.full_clean()
        except ValidationError:
            self.fail("Валидация не прошла для корректных данных")

    def test_periodicity_validator(self):
        """Тест валидатора периодичности"""
        # Проверка, что валидные значения не вызывают ошибок
        try:
            validate_periodicity(1)
            validate_periodicity(3)
            validate_periodicity(7)
        except ValidationError:
            self.fail("validate_periodicity вызвал ошибку для допустимых значений")

    def test_habit_model_save_method(self):
        """Тест метода save модели Habit"""
        # Тест с максимально допустимой продолжительностью
        habit = Habit(
            user=self.user,
            name='Тест',
            place='Дом',
            action='Тест сохранения',
            estimated_duration=120,
            time_to_complete='10:00'
        )
        habit.save()
        self.assertEqual(habit.estimated_duration, 120)

    def test_habit_validation_when_both_pleasant_and_reward(self):
        """Тест валидации приятной привычки с наградой"""
        with self.assertRaises(ValidationError):
            habit = Habit(
                user=self.user,
                name='Ошибочная привычка',
                place='Дом',
                action='Тест',
                is_pleasant=True,
                reward="Награда",  # Не должно быть награды у приятной привычки
                time_to_complete='10:00'
            )
            habit.full_clean()

    def test_habit_with_related_habit(self):
        """Тест привычки со связанной приятной привычкой"""
        pleasant_habit = Habit.objects.create(
            user=self.user,
            name='Приятная привычка',
            place='Дом',
            action='Смотреть фильм',
            is_pleasant=True,
            time_to_complete='10:00'
        )

        habit_with_related = Habit(
            user=self.user,
            name='Привычка со связанной',
            place='Дом',
            action='Делать что-то',
            related_habit=pleasant_habit,
            time_to_complete='11:00'
        )

        try:
            habit_with_related.full_clean()
            habit_with_related.save()
            self.assertEqual(habit_with_related.related_habit, pleasant_habit)
        except ValidationError:
            self.fail("Валидация не прошла для корректной связанной привычки")


class HabitCompletionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создание пользователя и привычки
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.habit = Habit.objects.create(
            user=cls.user,
            name='Тестовая привычка',
            place='Дом',
            action='Отжимания',
            periodicity=1,
            estimated_duration=5,
            time_to_complete='10:00'
        )

    def test_habit_completion_creation(self):
        """Тест создания записи о выполнении привычки"""
        completion = HabitCompletion.objects.create(
            habit=self.habit,
            user=self.habit.user,
            completed_at=timezone.now()
        )

        self.assertEqual(completion.habit, self.habit)
        self.assertIsNotNone(completion.completed_at)

    def test_habit_completion_str_method(self):
        """Тест строкового представления выполнения привычки"""
        completion = HabitCompletion.objects.create(
            habit=self.habit,
            user=self.habit.user,
            completed_at=timezone.now()
        )
        expected_str = f"{self.habit.name} ({completion.completed_at})"
        self.assertEqual(str(completion), expected_str)

    def test_habit_completion_with_notes(self):
        """Тест создания записи о выполнении привычки с примечанием"""
        notes = "Выполнил 20 отжиманий"
        completion = HabitCompletion.objects.create(
            habit=self.habit,
            user=self.habit.user,
            completed_at=timezone.now(),
            notes=notes,
            is_successful=False
        )

        self.assertEqual(completion.notes, notes)
        self.assertFalse(completion.is_successful)

    def test_habit_completion_default_values(self):
        """Тест значений по умолчанию для выполнения привычки"""
        completion = HabitCompletion(
            habit=self.habit,
            user=self.habit.user,
            completed_at=timezone.now()
        )
        completion.save()

        self.assertTrue(completion.is_successful)
        self.assertIsNone(completion.notes)

    def test_habit_estimated_duration_limit(self):
        """Тест ограничения продолжительности привычки"""
        habit = Habit.objects.create(
            user=self.user,
            name='Привычка с макс. продолжительностью',
            place='Дом',
            action='Долгое действие',
            estimated_duration=120,  # Максимальное значение
            time_to_complete='10:00'
        )
        self.assertEqual(habit.estimated_duration, 120)

    def test_validators_edge_cases(self):
        """Тест граничных случаев валидаторов"""
        # Проверка validate_periodicity для значения 7 (на границе)
        try:
            validate_periodicity(7)
        except ValidationError:
            self.fail("validate_periodicity вызвал ошибку для значения 7")

        # Проверка валидации длительности
        try:
            validate_duration(120)  # Верхняя граница
        except ValidationError:
            self.fail("validate_duration вызвал ошибку для допустимого значения")

        # Проверка валидации награды с пустой строкой
        try:
            validate_reward("", None)
        except ValidationError:
            self.fail("validate_reward вызвал ошибку для пустой строки")