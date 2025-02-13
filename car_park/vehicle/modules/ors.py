import requests

KEY = "5b3ce3597851110001cf62489efd2bfc610f4a348f0719877a5d6a56"


def reverse_geocode_ors(api_key: str, lat: str, lng: str):
    """
    Обратное геокодирование через ORS /geocode/reverse
    https://openrouteservice.org/dev/#/api-docs/geocode/reverse
    """
    if not api_key:
        return None

    url = "https://api.openrouteservice.org/geocode/reverse"
    params = {
        'api_key': api_key,
        'point.lat': lat,
        'point.lon': lng,
        'size': 1,
        'sources': 'osm'
    }
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        # например, data['features'][0]['properties']['label']
        address = data['features'][0]['properties'].get('label')
        return address
    except Exception as e:
        return None
