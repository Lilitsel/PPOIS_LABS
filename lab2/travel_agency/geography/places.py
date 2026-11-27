"""Географические объекты: страны, города, адреса, достопримечательности."""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from travel_agency.constants import (
    EARTH_RADIUS_KM,
    FIRST_MONTH,
    GROUP_DISCOUNT_MIN_SIZE,
    GROUP_DISCOUNT_PERCENT,
    LAST_MONTH,
    MAX_SAFE_TRAVEL_LEVEL,
    PERCENT_BASE,
)
from travel_agency.exceptions import InvalidTourDataException

if TYPE_CHECKING:
    from travel_agency.documents.identity import Passport


class Country:
    """Страна с визовым режимом и уровнем безопасности."""

    def __init__(self, name: str, iso_code: str, currency: str, safety_level: int = 1):
        self.name = name
        self.iso_code = iso_code.upper()
        self.currency = currency
        self.safety_level = safety_level
        self.visa_free_for: set[str] = set()

    def add_visa_free_country(self, iso_code: str) -> None:
        self.visa_free_for.add(iso_code.upper())

    def requires_visa_for(self, passport: Passport) -> bool:
        issuer = passport.issuing_country
        return issuer is not self and issuer.iso_code not in self.visa_free_for

    def is_safe_for_travel(self) -> bool:
        return self.safety_level <= MAX_SAFE_TRAVEL_LEVEL


class City:
    """Город с часовым поясом и координатами."""

    def __init__(self, name: str, country: Country, utc_offset_hours: int, latitude: float, longitude: float):
        self.name = name
        self.country = country
        self.utc_offset_hours = utc_offset_hours
        self.latitude = latitude
        self.longitude = longitude

    def local_time(self, utc_time: datetime) -> datetime:
        return utc_time + timedelta(hours=self.utc_offset_hours)

    def distance_to(self, other: City) -> float:
        """Расстояние по дуге большого круга (формула гаверсинусов), км."""
        lat1, lat2 = math.radians(self.latitude), math.radians(other.latitude)
        delta_lat = lat2 - lat1
        delta_lon = math.radians(other.longitude - self.longitude)
        haversine = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(haversine))


class Address:
    """Почтовый адрес."""

    def __init__(self, street: str, building: str, postal_code: str, city: City):
        self.street = street
        self.building = building
        self.postal_code = postal_code
        self.city = city

    def format_full(self) -> str:
        return f"{self.street}, {self.building}, {self.postal_code}, {self.city.name}"


class Attraction:
    """Достопримечательность с режимом работы и платой за вход."""

    def __init__(self, name: str, city: City, category: str, entrance_fee: float, opening_hour: int, closing_hour: int):
        self.name = name
        self.city = city
        self.category = category
        self.entrance_fee = entrance_fee
        self.opening_hour = opening_hour
        self.closing_hour = closing_hour

    def is_open_at(self, hour: int) -> bool:
        return self.opening_hour <= hour < self.closing_hour

    def calculate_group_fee(self, group_size: int) -> float:
        total = self.entrance_fee * group_size
        if group_size >= GROUP_DISCOUNT_MIN_SIZE:
            total *= (PERCENT_BASE - GROUP_DISCOUNT_PERCENT) / PERCENT_BASE
        return total


class Destination:
    """Туристическое направление: город, климат и что посмотреть."""

    def __init__(self, city: City, climate: str, best_months: set[int]):
        if any(not FIRST_MONTH <= month <= LAST_MONTH for month in best_months):
            raise InvalidTourDataException("Номер месяца должен быть от 1 до 12")
        self.city = city
        self.climate = climate
        self.best_months = best_months
        self.attractions: list[Attraction] = []

    @property
    def country(self) -> Country:
        return self.city.country

    def is_recommended_in_month(self, month: int) -> bool:
        return month in self.best_months

    def add_attraction(self, attraction: Attraction) -> None:
        if attraction.city is not self.city:
            raise InvalidTourDataException(f"{attraction.name} находится не в городе {self.city.name}")
        self.attractions.append(attraction)

    def find_attractions_by_category(self, category: str) -> list[Attraction]:
        return [attraction for attraction in self.attractions if attraction.category == category]
