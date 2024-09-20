from django.db import models


# Create your models here.

class Vehicle(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')
    release_year = models.PositiveIntegerField(verbose_name='Год выпуска')
    mileage = models.PositiveIntegerField(verbose_name='Пробег')
    color = models.CharField(max_length=50, verbose_name='Цвет')
    transmission_type = models.CharField(max_length=50, verbose_name='Тип трансмиссии')

    def __str__(self):
        return f"{self.release_year} Vehicle"
