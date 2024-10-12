from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


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
