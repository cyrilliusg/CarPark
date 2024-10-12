from django.contrib import admin

# Register your models here.

from .models import Vehicle, Brand, Model, Configuration, Enterprise, Driver, VehicleDriverAssignment


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


class VehicleDriverAssignmentInline(admin.TabularInline):
    model = VehicleDriverAssignment
    extra = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'vin', 'configuration', 'enterprise', 'release_year', 'price', 'transmission_type')
    list_filter = ('enterprise', 'configuration__model__brand', 'release_year', 'transmission_type')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.drivers.exists():
            return ['enterprise']
        return []


@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'enterprise', 'salary')
    list_filter = ('enterprise',)
    inlines = [VehicleDriverAssignmentInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.vehicles.exists():
            return ['enterprise']
        return []



@admin.register(VehicleDriverAssignment)
class VehicleDriverAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'driver', 'is_active')
    list_filter = ('is_active', 'driver', 'vehicle')
