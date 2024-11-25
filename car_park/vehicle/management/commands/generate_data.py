import random
from django.core.management.base import BaseCommand
from faker import Faker
from ...models import Brand, Model, Configuration, Enterprise, Vehicle, Driver, VehicleDriverAssignment

fake = Faker()


class Command(BaseCommand):
    help = "Генерация случайных данных для предприятий, машин и водителей."

    # def add_arguments(self, parser):
    #     parser.add_argument('enterprise_count', type=int, help="Количество предприятий")
    #     parser.add_argument('vehicle_count', type=int, help="Количество машин для каждого предприятия")
    #     parser.add_argument('driver_count', type=int, help="Количество водителей для каждого предприятия")

    # def handle(self, *args, **options):
    #     enterprise_count = options['enterprise_count']
    #     vehicle_count = options['vehicle_count']
    #     driver_count = options['driver_count']
    #
    #     # Генерация брендов, моделей и комплектаций
    #     brands = []
    #     for _ in range(5):
    #         brand = Brand.objects.create(name=fake.unique.company(), country=fake.country())
    #         for _ in range(3):
    #             model = Model.objects.create(
    #                 name=fake.word(),
    #                 brand=brand,
    #                 vehicle_type=random.choice([choice[0] for choice in Model.VEHICLE_TYPE_CHOICES]),
    #             )
    #             for _ in range(2):
    #                 Configuration.objects.create(
    #                     model=model,
    #                     name=fake.word(),
    #                     tank_capacity=random.uniform(40, 80),
    #                     payload=random.randint(500, 3000),
    #                     seats_number=random.randint(2, 7),
    #                 )
    #         brands.append(brand)
    #
    #     # Генерация предприятий, машин и водителей
    #     enterprises = []
    #     for _ in range(enterprise_count):
    #         enterprise = Enterprise.objects.create(
    #             name=fake.unique.company(),
    #             city=fake.city()
    #         )
    #         enterprises.append(enterprise)
    #
    #         # Генерация машин
    #         configurations = Configuration.objects.all()
    #         for _ in range(vehicle_count):
    #             vehicle = Vehicle.objects.create(
    #                 vin=fake.unique.bothify('??#####??#####'),
    #                 price=random.uniform(10000, 100000),
    #                 release_year=random.randint(2000, 2023),
    #                 mileage=random.randint(0, 300000),
    #                 color=fake.color_name(),
    #                 transmission_type=random.choice([choice[0] for choice in Vehicle.TRANSMISSION_CHOICES]),
    #                 configuration=random.choice(configurations),
    #                 enterprise=enterprise,
    #             )
    #
    #         # Генерация водителей
    #         for _ in range(driver_count):
    #             driver = Driver.objects.create(
    #                 name=fake.name(),
    #                 salary=random.uniform(50000, 150000),
    #                 enterprise=enterprise,
    #             )
    #             if random.randint(1, 10) == 1:
    #                 # Привязываем активного водителя к случайной машине
    #                 vehicle = random.choice(Vehicle.objects.filter(enterprise=enterprise))
    #                 assignment = VehicleDriverAssignment.objects.create(
    #                     vehicle=vehicle,
    #                     driver=driver,
    #                     is_active=True,
    #                 )
    #
    #     # Вывод результатов
    #     self.stdout.write(self.style.SUCCESS(
    #         f'Создано: {enterprise_count} предприятий, {enterprise_count * vehicle_count} машин, {enterprise_count * driver_count} водителей.'
    #     ))

    def handle(self, *args, **options):
        # Удаляем все существующие данные
        VehicleDriverAssignment.objects.all().delete()
        Vehicle.objects.all().delete()
        Driver.objects.all().delete()
        Enterprise.objects.all().delete()
        Configuration.objects.all().delete()
        Model.objects.all().delete()
        Brand.objects.all().delete()

        # Генерация брендов и моделей
        self.stdout.write("Генерация брендов и моделей...")
        brands = []
        for _ in range(5):  # создаем 5 брендов
            brand = Brand.objects.create(
                name=fake.unique.company(),
                country=fake.country()
            )
            brands.append(brand)

        configurations = []
        for brand in brands:
            for _ in range(10):  # у каждого бренда 10 моделей
                model = Model.objects.create(
                    name=fake.unique.word(),
                    brand=brand,
                    vehicle_type=random.choice([choice[0] for choice in Model.VEHICLE_TYPE_CHOICES])
                )
                for _ in range(3):  # у каждой модели 3 конфигурации
                    configuration = Configuration.objects.create(
                        model=model,
                        name=fake.word(),
                        tank_capacity=random.uniform(40, 80),
                        payload=random.randint(500, 3000),
                        seats_number=random.randint(2, 7)
                    )
                    configurations.append(configuration)

        # Генерация предприятий
        self.stdout.write("Генерация предприятий...")
        enterprises = []
        for _ in range(3):  # создаем 3 предприятия
            enterprise = Enterprise.objects.create(
                name=fake.unique.company(),
                city=fake.city()
            )
            enterprises.append(enterprise)

        # Генерация машин и водителей
        self.stdout.write("Генерация машин и водителей...")
        for enterprise in enterprises:
            drivers = []
            for _ in range(300):  # создаем 300 водителей на предприятие
                driver = Driver.objects.create(
                    name=fake.name(),
                    salary=random.uniform(50000, 120000),
                    enterprise=enterprise
                )
                drivers.append(driver)

            for i in range(random.randint(3000, 5000)):  # создаем 3000–5000 машин на предприятие
                vehicle = Vehicle.objects.create(
                    vin=fake.unique.bothify('??####??##??####'),
                    price=random.uniform(1000000, 5000000),
                    release_year=random.randint(2000, 2023),
                    mileage=random.randint(0, 300000),
                    color=fake.color_name(),
                    transmission_type=random.choice([choice[0] for choice in Vehicle.TRANSMISSION_CHOICES]),
                    configuration=random.choice(configurations),
                    enterprise=enterprise
                )

                # Каждая 10-я машина получает активного водителя
                if i % 10 == 0:
                    driver = random.choice(drivers)
                    VehicleDriverAssignment.objects.create(
                        vehicle=vehicle,
                        driver=driver,
                        is_active=True
                    )

        self.stdout.write(self.style.SUCCESS("Генерация данных завершена!"))
