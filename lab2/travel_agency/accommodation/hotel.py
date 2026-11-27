"""Отели, номера, планы питания и бронирование проживания."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from travel_agency.documents.identity import ensure_date_order
from travel_agency.exceptions import InvalidBookingStateException, InvalidTourDataException, RoomNotAvailableException

if TYPE_CHECKING:
    from travel_agency.geography.places import Address
    from travel_agency.people.person import Client


class RoomType:
    """Категория номера, влияющая на цену."""

    def __init__(self, name: str, price_multiplier: float, has_balcony: bool):
        self.name = name
        self.price_multiplier = price_multiplier
        self.has_balcony = has_balcony

    def apply_multiplier(self, base_price: float) -> float:
        return base_price * self.price_multiplier


class MealPlan:
    """Тип питания: BB, HB, AI и т. п."""

    def __init__(self, code: str, daily_cost_per_person: float, meals_per_day: int):
        self.code = code
        self.daily_cost_per_person = daily_cost_per_person
        self.meals_per_day = meals_per_day

    def calculate_cost(self, guests: int, nights: int) -> float:
        return self.daily_cost_per_person * guests * nights


class Room:
    """Гостиничный номер."""

    def __init__(self, number: str, room_type: RoomType, capacity: int, base_price_per_night: float):
        self.number = number
        self.room_type = room_type
        self.capacity = capacity
        self.base_price_per_night = base_price_per_night
        self.is_available = True

    @property
    def price_per_night(self) -> float:
        return self.room_type.apply_multiplier(self.base_price_per_night)

    def calculate_stay_cost(self, nights: int) -> float:
        return self.price_per_night * nights

    def can_accommodate(self, guests: int) -> bool:
        return self.is_available and guests <= self.capacity


class Hotel:
    """Отель-партнёр компании."""

    def __init__(self, name: str, address: Address, stars: int, check_in_hour: int):
        self.name = name
        self.address = address
        self.stars = stars
        self.check_in_hour = check_in_hour
        self.rooms: dict[str, Room] = {}
        self.meal_plans: dict[str, MealPlan] = {}

    def add_room(self, room: Room) -> None:
        if room.number in self.rooms:
            raise InvalidTourDataException(f"Номер {room.number} уже есть в отеле {self.name}")
        self.rooms[room.number] = room

    def add_meal_plan(self, meal_plan: MealPlan) -> None:
        self.meal_plans[meal_plan.code] = meal_plan

    def find_available_room(self, guests: int) -> Room:
        suitable = [room for room in self.rooms.values() if room.can_accommodate(guests)]
        if not suitable:
            raise RoomNotAvailableException(f"В отеле {self.name} нет свободного номера на {guests} гостей")
        return min(suitable, key=lambda room: room.price_per_night)

    def reserve_room(self, client: Client, guests: int, check_in: date, check_out: date) -> HotelReservation:
        room = self.find_available_room(guests)
        reservation = HotelReservation(self, room, client, guests, (check_in, check_out))
        room.is_available = False
        return reservation

    def release_room(self, room_number: str) -> None:
        self.rooms[room_number].is_available = True

    def count_free_rooms(self) -> int:
        return sum(1 for room in self.rooms.values() if room.is_available)


class HotelReservation:
    """Бронь номера на период проживания."""

    def __init__(self, hotel: Hotel, room: Room, client: Client, guests: int, stay_period: tuple[date, date]):
        check_in, check_out = stay_period
        ensure_date_order(check_in, check_out)
        self.hotel = hotel
        self.room = room
        self.client = client
        self.guests = guests
        self.check_in = check_in
        self.check_out = check_out
        self.meal_plan: Optional[MealPlan] = None
        self.is_cancelled = False

    def calculate_nights(self) -> int:
        return (self.check_out - self.check_in).days

    def choose_meal_plan(self, code: str) -> None:
        if code not in self.hotel.meal_plans:
            raise InvalidTourDataException(f"Отель {self.hotel.name} не предлагает питание {code}")
        self.meal_plan = self.hotel.meal_plans[code]

    def calculate_total(self) -> float:
        nights = self.calculate_nights()
        total = self.room.calculate_stay_cost(nights)
        if self.meal_plan is not None:
            total += self.meal_plan.calculate_cost(self.guests, nights)
        return total

    def cancel(self) -> None:
        if self.is_cancelled:
            raise InvalidBookingStateException("Бронь отеля уже отменена")
        self.hotel.release_room(self.room.number)
        self.is_cancelled = True
