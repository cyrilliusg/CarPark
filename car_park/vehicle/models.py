from django.db import models


# Create your models here.

class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    vin = models.CharField(max_length=17, unique=True, verbose_name='VIN')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')
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

    def __str__(self):
        return f"{self.release_year} Vehicle"
