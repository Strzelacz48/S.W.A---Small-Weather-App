import logging

import requests
from django.core.cache import cache

from .models import CityCoordinate

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Identifies this app to Nominatim, as required by their usage policy
# (https://operations.osmfoundation.org/policies/nominatim/) — requests
# without a descriptive User-Agent can be blocked outright.
NOMINATIM_USER_AGENT = "contacts-manager-recruitment-task/1.0 (+marc.czapulak@gmail.com)"

REQUEST_TIMEOUT_SECONDS = 5

WEATHER_CACHE_TTL_SECONDS = 60 * 45  # 45 min, within the requested 30-60 min window
GEOCODE_FAILURE_CACHE_TTL_SECONDS = 60 * 5  # short TTL so a bad city name doesn't hammer Nominatim


def geocode_city(city):
    """Return (latitude, longitude) for a city name, or None if it can't be resolved.

    Results are persisted in CityCoordinate so a given city is only ever
    sent to Nominatim once, regardless of how many contacts share it or
    how many times the in-memory cache is cleared/restarted.
    """
    city = city.strip()
    if not city:
        return None

    existing = CityCoordinate.objects.filter(name__iexact=city).first()
    if existing:
        return existing.latitude, existing.longitude

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": NOMINATIM_USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        results = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Geocoding failed for city %r: %s", city, exc)
        return None

    if not results:
        logger.info("Nominatim found no coordinates for city %r", city)
        return None

    latitude = float(results[0]["lat"])
    longitude = float(results[0]["lon"])
    CityCoordinate.objects.create(name=city, latitude=latitude, longitude=longitude)
    return latitude, longitude


def get_weather_for_city(city):
    """Return {temperature, humidity, wind_speed} for a city, or None on failure.

    Cached per city for WEATHER_CACHE_TTL_SECONDS, so repeated page loads
    within the cache window never re-hit Open-Meteo (or Nominatim, since
    geocoding is looked up first and is itself skipped once cached in the DB).
    """
    city = city.strip()
    cache_key = f"weather:{city.lower()}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached or None  # cached falsy sentinel means "known failure"

    coordinates = geocode_city(city)
    if coordinates is None:
        cache.set(cache_key, False, GEOCODE_FAILURE_CACHE_TTL_SECONDS)
        return None

    latitude, longitude = coordinates

    try:
        response = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        current = response.json()["current"]
    except (requests.RequestException, ValueError, KeyError) as exc:
        logger.warning("Weather fetch failed for city %r: %s", city, exc)
        cache.set(cache_key, False, GEOCODE_FAILURE_CACHE_TTL_SECONDS)
        return None

    weather = {
        "temperature_c": current["temperature_2m"],
        "humidity_percent": current["relative_humidity_2m"],
        "wind_speed_kmh": current["wind_speed_10m"],
    }
    cache.set(cache_key, weather, WEATHER_CACHE_TTL_SECONDS)
    return weather