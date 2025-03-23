import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.gis.db import models as gis_models
from haversine import haversine

from timezone_field import TimeZoneField

from .modules.gps_math import get_period_key


# Create your models here.

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название бренда')
    country = models.CharField(max_length=100, verbose_name='Страна')

    def __str__(self):
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название модели')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models', verbose_name='Бренд')

    VEHICLE_TYPE_CHOICES = [
        ('Passenger', 'Легковой'),
        ('Truck', 'Грузовой'),
        ('Bus', 'Автобус'),
        ('SUV', 'Внедорожник'),
        ('Van', 'Фургон'),
    ]

    vehicle_type = models.CharField(max_length=50,
                                    choices=VEHICLE_TYPE_CHOICES,
                                    verbose_name='Тип транспортного средства')

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Configuration(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='configurations', verbose_name='Модель')
    name = models.CharField(max_length=100, verbose_name='Название комплектации')
    tank_capacity = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(0.0)],
                                        verbose_name='Объем бака (л)')
    payload = models.PositiveIntegerField(verbose_name='Грузоподъемность (кг)')
    seats_number = models.PositiveIntegerField(verbose_name='Количество мест')

    def __str__(self):
        return f"{self.model} - {self.name}"


class Enterprise(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название предприятия')
    city = models.CharField(max_length=100, verbose_name='Город')

    local_timezone = TimeZoneField(
        default='UTC',
        verbose_name='Локальная таймзона'
    )
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name


class Driver(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя водителя')
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Зарплата')
    enterprise = models.ForeignKey(Enterprise,
                                   on_delete=models.CASCADE,
                                   related_name='drivers',
                                   verbose_name='Предприятие'
                                   )

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    vin = models.CharField(max_length=17, unique=True, verbose_name='VIN')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)],
                                verbose_name='Стоимость')
    release_year = models.PositiveIntegerField(verbose_name='Год выпуска')
    mileage = models.PositiveIntegerField(verbose_name='Пробег')
    color = models.CharField(max_length=50, verbose_name='Цвет')

    MECHANICAL = 'Механическая'
    AUTOMATIC = 'Автоматическая'
    CVT = 'Бесступенчатая'
    ROBOTIC = 'Роботизированная'
    SEQUENTIAL = 'Последовательная механическая и полуавтоматическая'

    TRANSMISSION_CHOICES = [
        (MECHANICAL, 'Механические'),
        (AUTOMATIC, 'Автоматические'),
        (CVT, 'Бесступенчатые'),
        (ROBOTIC, 'Роботизированные'),
        (SEQUENTIAL, 'Последовательные механические и полуавтоматические'),
    ]

    transmission_type = models.CharField(
        max_length=50,
        choices=TRANSMISSION_CHOICES,
        default=MECHANICAL,
        verbose_name='Тип трансмиссии'
    )

    configuration = models.ForeignKey(Configuration,
                                      on_delete=models.CASCADE,
                                      related_name='vehicles',
                                      verbose_name='Комплектация')

    enterprise = models.ForeignKey(Enterprise,
                                   on_delete=models.CASCADE,
                                   related_name='vehicles',
                                   verbose_name='Предприятие',
                                   )

    drivers = models.ManyToManyField(Driver,
                                     through='VehicleDriverAssignment',
                                     related_name='vehicles',
                                     verbose_name='Водители'
                                     )
    purchase_datetime = models.DateTimeField(
        default=timezone.now,  # хранится в UTC, если USE_TZ = True
        verbose_name='Дата/время покупки (UTC)'
    )

    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.configuration.model.brand.name} {self.configuration.model.name} (VIN: {self.vin})"


class VehicleDriverAssignment(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, verbose_name='Автомобиль')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Водитель')
    is_active = models.BooleanField(default=False, verbose_name='Активный водитель')

    class Meta:
        unique_together = ('vehicle', 'driver')

    def clean(self):
        if self.is_active:
            # Проверяем, что водитель не является активным на другом автомобиле
            active_assignments = VehicleDriverAssignment.objects.filter(
                driver=self.driver,
                is_active=True
            ).exclude(pk=self.pk)
            if active_assignments.exists():
                raise ValidationError('Этот водитель уже активен на другом автомобиле.')

            # Проверяем, что на автомобиле нет другого активного водителя
            active_assignments = VehicleDriverAssignment.objects.filter(
                vehicle=self.vehicle,
                is_active=True
            ).exclude(pk=self.pk)
            if active_assignments.exists():
                raise ValidationError('У этого автомобиля уже есть активный водитель.')

    def __str__(self):
        return f"{self.driver.name} assigned to {self.vehicle}"


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    nickname = models.CharField(max_length=100, null=True, blank=True)
    enterprises = models.ManyToManyField('Enterprise', related_name='managers', verbose_name='Предприятия')

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class VehicleGPSPoint(gis_models.Model):
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='gps_points')
    timestamp = models.DateTimeField(default=timezone.now)
    location = gis_models.PointField()  # хранит точку (ш/д)

    class Meta:
        ordering = ['timestamp']
        verbose_name = "GPS точка автомобиля"
        verbose_name_plural = "GPS точки автомобилей"

    def __str__(self):
        return f"{self.vehicle} @ {self.timestamp} ({self.location})"


class Route(models.Model):
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='routes')
    start_time = models.DateTimeField()  # UTC
    end_time = models.DateTimeField()  # UTC
    # Допустим, храним интервал (duration). PostgreSQL-специфичный тип "interval":
    duration = models.DurationField(null=True, blank=True)

    # Координаты начала/конца
    start_location = gis_models.PointField( null=True, blank=True)
    end_location = gis_models.PointField(null=True, blank=True)

    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Route for {self.vehicle} ({self.start_time} - {self.end_time})"


class Report(models.Model):
    """
    Базовая модель отчёта.
    Можно сделать abstract=True, если вы никогда не будете её инстанцировать напрямую.
    Но если хотите иметь 'общие' отчёты, пусть будет полноценной.
    """
    name = models.CharField(max_length=255, verbose_name="Название отчёта")
    start_date = models.DateField()
    end_date = models.DateField()

    PERIOD_CHOICES = [
        ('day', 'День'),
        ('month', 'Месяц'),
        ('year', 'Год'),
    ]
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)

    # Результат в виде массива/словаря "дата" => "значение"
    # Можно хранить [{"date": "...", "value": ...}, ...] или более сложную структуру
    result = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # Если хотим привязать к пользователю-автору
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report {self.name} [{self.start_date} - {self.end_date}] {self.period} {self.result} {self.created_at}"


class VehicleMileageReport(Report):
    """
    Пример конкретного отчёта о пробеге автомобиля.
    """
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='mileage_reports')

    # Дополнительные поля?
    # total_mileage = models.PositiveIntegerField(default=0)

    def calculate_report(self):
        """
        Здесь можно сделать вычисление пробега по GPS-точкам / маршрутам.
        По итогу записать self.result = [...], self.save()
        """
        # Логика: берем start_date, end_date, period => делаем агрегацию.
        # Считаем, например, суммарный километраж по дням/месяцам.
        # self.result = [{"date": "2025-01-01", "mileage": 123}, ...]

        # Пример.
        points = VehicleGPSPoint.objects.filter(
            vehicle=self.vehicle,
            timestamp__date__gte=self.start_date,
            timestamp__date__lte=self.end_date
        ).order_by('timestamp')
        # Считаем накопительный пробег
        total = 0.0
        prev = None
        daily_data = {}
        for p in points:
            if prev:
                dist = haversine((prev.location.y, prev.location.x), (p.location.y, p.location.x))
                # dist в км
                # dayKey = p.timestamp.date() (если period='day')
                dayKey = get_period_key(p.timestamp, self.period)  # day/month/year
                daily_data[dayKey] = daily_data.get(dayKey, 0) + dist
            prev = p
        # Превращаем dict -> list
        self.result = [{"date": k, "mileage": v} for k, v in daily_data.items()]
        # self.save()






