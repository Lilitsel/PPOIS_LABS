"""Туры, сезоны, программа по дням и экскурсии."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from travel_agency.constants import (
    DEFAULT_COEFFICIENT,
    FIRST_MONTH,
    GROUP_TOUR_DISCOUNT_PERCENT,
    LAST_MONTH,
    MAX_ACTIVE_HOURS_PER_DAY,
    PERCENT_BASE,
)
from travel_agency.exceptions import CapacityExceededException, InvalidTourDataException, TourFullyBookedException

if TYPE_CHECKING:
    from travel_agency.geography.places import Attraction, City, Destination
    from travel_agency.people.person import Client
    from travel_agency.people.staff import Guide
    from travel_agency.service.clients import Review


class Season:
    """Сезон с ценовым коэффициентом; может переходить через Новый год."""

    def __init__(self, name: str, start_month: int, end_month: int, price_coefficient: float):
        for month in (start_month, end_month):
            if not FIRST_MONTH <= month <= LAST_MONTH:
                raise InvalidTourDataException(f"Некорректный месяц: {month}")
        self.name = name
        self.start_month = start_month
        self.end_month = end_month
        self.price_coefficient = price_coefficient

    def contains_date(self, day: date) -> bool:
        if self.start_month <= self.end_month:
            return self.start_month <= day.month <= self.end_month
        return day.month >= self.start_month or day.month <= self.end_month

    def adjust_price(self, price: float) -> float:
        return price * self.price_coefficient


class Excursion:
    """Экскурсия к достопримечательности с ограниченным числом мест."""

    def __init__(self, name: str, attraction: Attraction, language: str, duration_hours: float,
                 price_per_person: float, max_participants: int):
        self.name = name
        self.attraction = attraction
        self.language = language
        self.duration_hours = duration_hours
        self.price_per_person = price_per_person
        self.max_participants = max_participants
        self.guide: Optional[Guide] = None
        self.participants: list[Client] = []

    def is_full(self) -> bool:
        return len(self.participants) >= self.max_participants

    def register_participant(self, client: Client) -> None:
        if client in self.participants:
            return
        if self.is_full():
            raise CapacityExceededException(f"На экскурсии «{self.name}» нет мест")
        self.participants.append(client)

    def calculate_revenue(self) -> float:
        tickets_revenue = self.price_per_person * len(self.participants)
        entrance_cost = self.attraction.calculate_group_fee(len(self.participants))
        return tickets_revenue - entrance_cost


class ItineraryDay:
    """Один день программы тура."""

    def __init__(self, day_number: int, city: City, free_time_hours: float):
        self.day_number = day_number
        self.city = city
        self.free_time_hours = free_time_hours
        self.excursions: list[Excursion] = []

    def calculate_busy_hours(self) -> float:
        return sum(excursion.duration_hours for excursion in self.excursions)

    def add_excursion(self, excursion: Excursion) -> None:
        if self.calculate_busy_hours() + excursion.duration_hours > MAX_ACTIVE_HOURS_PER_DAY:
            raise InvalidTourDataException(f"День {self.day_number} перегружен экскурсиями")
        self.excursions.append(excursion)


class Itinerary:
    """Программа тура по дням."""

    def __init__(self):
        self.days: list[ItineraryDay] = []
        self.total_distance_km = 0.0

    def add_day(self, day: ItineraryDay) -> None:
        if day.day_number != len(self.days) + 1:
            raise InvalidTourDataException(f"Ожидался день №{len(self.days) + 1}")
        if self.days:
            self.total_distance_km += self.days[-1].city.distance_to(day.city)
        self.days.append(day)

    def remove_last_day(self) -> ItineraryDay:
        if not self.days:
            raise InvalidTourDataException("Программа тура пуста")
        removed = self.days.pop()
        if self.days:
            self.total_distance_km -= self.days[-1].city.distance_to(removed.city)
        return removed

    def count_activities(self) -> int:
        return sum(len(day.excursions) for day in self.days)


class Tour:
    """Тур по направлению с ограниченным числом мест."""

    def __init__(self, tour_id: str, name: str, destination: Destination, duration_days: int,
                 base_price: float, max_group_size: int):
        if duration_days <= 0 or base_price <= 0 or max_group_size <= 0:
            raise InvalidTourDataException("Длительность, цена и размер группы должны быть положительными")
        self.tour_id = tour_id
        self.name = name
        self.destination = destination
        self.duration_days = duration_days
        self.base_price = base_price
        self.max_group_size = max_group_size
        self.itinerary = Itinerary()
        self.seasons: list[Season] = []
        self.reviews: list[Review] = []
        self.booked_places = 0

    @property
    def destination_name(self) -> str:
        city = self.destination.city
        return city.name

    def add_season(self, season: Season) -> None:
        self.seasons.append(season)

    def season_coefficient(self, day: date) -> float:
        matching = [season.price_coefficient for season in self.seasons if season.contains_date(day)]
        return matching[0] if matching else DEFAULT_COEFFICIENT

    def is_available_in_season(self, day: date) -> bool:
        return any(season.contains_date(day) for season in self.seasons)

    def calculate_price_for_group(self, group_size: int, start_date: date) -> float:
        return self.base_price * group_size * self.season_coefficient(start_date)

    def free_places(self) -> int:
        return self.max_group_size - self.booked_places

    def has_free_places(self, places: int = 1) -> bool:
        return self.free_places() >= places

    def reserve_places(self, places: int) -> None:
        if not self.has_free_places(places):
            raise TourFullyBookedException(f"В туре «{self.name}» осталось мест: {self.free_places()}")
        self.booked_places += places

    def release_places(self, places: int) -> None:
        self.booked_places = max(0, self.booked_places - places)

    def add_review(self, review: Review) -> None:
        self.reviews.append(review)

    def average_rating(self) -> float:
        if not self.reviews:
            return 0.0
        return sum(review.rating for review in self.reviews) / len(self.reviews)


class GroupTour(Tour):
    """Групповой тур с руководителем группы и минимальным набором."""

    def __init__(self, tour: Tour, group_leader: Guide, min_participants: int):
        super().__init__(tour.tour_id, tour.name, tour.destination, tour.duration_days, tour.base_price, tour.max_group_size)
        if min_participants > self.max_group_size:
            raise InvalidTourDataException("Минимум участников больше вместимости тура")
        self.group_leader = group_leader
        self.min_participants = min_participants

    def is_confirmed(self) -> bool:
        return self.booked_places >= self.min_participants

    def calculate_price_for_group(self, group_size: int, start_date: date) -> float:
        full_price = super().calculate_price_for_group(group_size, start_date)
        return full_price * (PERCENT_BASE - GROUP_TOUR_DISCOUNT_PERCENT) / PERCENT_BASE
