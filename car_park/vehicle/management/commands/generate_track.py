import math
import random
import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point
from ...models import Vehicle, VehicleGPSPoint


class Command(BaseCommand):
    """
       Пример:
         python manage.py generate_track <vehicle_id> --distance=5 --start-lat=55.7558 --start-lng=37.6173 --delay=10 --api-key=YOUR_ORS_KEY

       --distance (км): желаемая длина трека
       --start-lat, --start-lng: координаты начальной точки
       --delay: базовый шаг псевдо-времени (сек), случайно умножаем +/- для разнообразия
       --api-key: ключ OpenRouteService

       Шаги:
       1) Определяем конечную точку (end_lat, end_lng) на расстоянии distance_km от start_lat/lng.
       2) Делаем запрос к ORS, получаем список coords [[lng, lat], [lng, lat], ...].
       3) Для каждой точки создаём VehicleGPSPoint с timestamp, который увеличиваем без реального time.sleep.
       """
    help = "Генерирует трек для указанной машины, добавляя GPS-точки в базу с имитацией реального времени (UTC)."

    def add_arguments(self, parser):
        parser.add_argument('vehicle_id', type=int, help="ID машины (Vehicle)")
        parser.add_argument('--distance', type=float, default=5.0, help="Длина маршрута (км) - для упрощенной логики.")
        parser.add_argument('--start-lat', type=float, default=55.7558, help="Начальная широта (lat)")
        parser.add_argument('--start-lng', type=float, default=37.6173, help="Начальная долгота (lng)")
        parser.add_argument('--delay', type=int, default=10,
                            help="Задержка (сек) между добавлением точек (имитация реального времени).")
        parser.add_argument('--api-key', type=str, default=None, help="OpenRouteService API key")

    def handle(self, *args, **options):
        vehicle_id = options['vehicle_id']
        distance_km = options['distance']
        start_lat = options['start_lat']
        start_lng = options['start_lng']
        delay_sec = options['delay']
        api_key = options['api_key']

        # 1) Проверяем машину
        try:
            vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
        except:
            raise CommandError(f"Vehicle with id={vehicle_id} not found.")

        self.stdout.write(self.style.SUCCESS(
            f"Генерация трека для машины ID={vehicle_id}, distance={distance_km} км "
            f"(начало [lat, lng]: {start_lat}, {start_lng})."
        ))

        # Шаг 1: Вычисляем конечную точку (end_lat, end_lng).
        bearing_deg, end_lat, end_lng = self.__calculate_end_point(distance_km, start_lat, start_lng)
        self.stdout.write(self.style.SUCCESS(
            f"Случайный bearing={bearing_deg:.2f}°, end [lat, lng]: {end_lat:.5f}, {end_lng:.5f}"
        ))

        # Шаг 2: Запрос к ORS
        if not api_key:
            raise CommandError("Для реального маршрута нужен --api-key=...")

        route_coords = self.__get_ors_route(api_key, start_lng, start_lat, end_lng, end_lat)

        # 3) Идём по route_coords, добавляя VehicleGPSPoint c задержкой
        if not route_coords:
            self.stdout.write(self.style.WARNING("Маршрут пуст, завершаем."))
            return

        self.stdout.write(self.style.SUCCESS(f"Получен маршрут из {len(route_coords)} точек от ORS."))

        # Шаг 3: добавляем VehicleGPSPoint c псевдо-временем
        current_time = timezone.now()
        for idx, (lng, lat) in enumerate(route_coords):
            # случайно варьируем приращение времени:
            random_delay = random.uniform(delay_sec * 0.5, delay_sec * 1.5)
            current_time += timezone.timedelta(seconds=random_delay)
            # Сохраняем точку
            VehicleGPSPoint.objects.create(
                vehicle=vehicle,
                timestamp=current_time,
                location=Point(lng, lat, srid=4326)
            )
            self.stdout.write(f"[{idx + 1}/{len(route_coords)}] [lat, lng] => {lat:.5f}, {lng:.5f}, time={current_time}")

        self.stdout.write(self.style.SUCCESS("Трек успешно сгенерирован!"))

    def __calculate_end_point(self, distance_km, start_lat, start_lng) -> list[float]:
        """Вычисляем конечную точку (end_lat, end_lng).
        Упростим задачу: возьмём случайный азимут (bearing) и прибавим distance_km.
        Примерная формула: 1 градус широты ~ 111км, 1 градус долготы ~ 111км*cos(lat).
        """
        R = 6371.0  # Радиус Земли (км)

        bearing_deg = random.uniform(0, 360)
        bearing_rad = math.radians(bearing_deg)
        # delta_deg = distance_km / 111
        # Для долготы используем cos(lat):
        # Но лучше использовать чуть более точный подход.
        lat_rad = math.radians(start_lat)
        dist_frac = distance_km / R  # угловая дистанция
        # Формула прямой геодезической задачи:
        # lat2 = asin( sin(lat1)*cos(d/R) + cos(lat1)*sin(d/R)*cos(bearing) )
        # lon2 = lon1 + atan2( sin(bearing)*sin(d/R)*cos(lat1), cos(d/R)-sin(lat1)*sin(lat2) )
        lat2 = math.asin(math.sin(lat_rad) * math.cos(dist_frac) +
                         math.cos(lat_rad) * math.sin(dist_frac) * math.cos(bearing_rad))
        # считаем lon2
        lon1 = math.radians(start_lng)
        lon2 = lon1 + math.atan2(
            math.sin(bearing_rad) * math.sin(dist_frac) * math.cos(lat_rad),
            math.cos(dist_frac) - math.sin(lat_rad) * math.sin(lat2)
        )
        end_lat = math.degrees(lat2)
        end_lng = math.degrees(lon2)

        return [bearing_deg, end_lat, end_lng]

    def __get_ors_route(self,
                        api_key: str,
                        start_lng: float, start_lat: float,
                        end_lng: float, end_lat: float) -> list[[list[float]]]:
        """
        Запрашиваем маршрут у OpenRouteService (driving-car).
        Возвращаем список (lng, lat)
        Документация: https://openrouteservice.org/dev/#/api-docs
        """
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        params = {
            'api_key': api_key,
            # start и end - lon, lat
            'start': f"{start_lng},{start_lat}",
            'end': f"{end_lng},{end_lat}",
        }
        coordinates = []
        self.stdout.write(params)
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            # Разбираем geometry -> coordinates: [[lng, lat], [lng, lat], ...]
            coordinates = data['features'][0]['geometry']['coordinates']
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при запросе к ORS: {e}"))
        return coordinates
