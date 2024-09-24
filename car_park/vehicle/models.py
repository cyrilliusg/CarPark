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
    tank_capacity = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(0.0)], verbose_name='Объем бака (л)')
    payload = models.PositiveIntegerField(verbose_name='Грузоподъемность (кг)')
    seats_number = models.PositiveIntegerField(verbose_name='Количество мест')

    def __str__(self):
        return f"{self.model} - {self.name}"


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    vin = models.CharField(max_length=17, unique=True, verbose_name='VIN')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)], verbose_name='Стоимость')
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

    def __str__(self):
        return f"{self.release_year} Vehicle"
