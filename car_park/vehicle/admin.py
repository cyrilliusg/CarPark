from django.contrib import admin

# Register your models here.

from .models import Vehicle, Brand, Model, Configuration

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'vehicle_type')
    list_filter = ('brand', 'vehicle_type')

@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'model', 'tank_capacity', 'payload', 'seats_number')
    list_filter = ('model',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'vin', 'configuration', 'release_year', 'price', 'transmission_type')
    list_filter = ('configuration__model__brand', 'release_year', 'transmission_type')
