"""Автобусы и трансферы."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from travel_agency.constants import AVERAGE_BUS_SPEED_KMH, TRANSFER_BASE_COST, TRANSFER_COST_PER_KM
from travel_agency.exceptions import CapacityExceededException, InvalidBookingStateException

if TYPE_CHECKING:
    from travel_agency.geography.places import Address
    from travel_agency.people.person import Client
    from travel_agency.people.staff import Driver


class Bus:
    """Автобус компании."""

    def __init__(self, plate_number: str, capacity: int, required_license: str, has_air_conditioning: bool):
        self.plate_number = plate_number
        self.capacity = capacity
        self.required_license = required_license.upper()
        self.has_air_conditioning = has_air_conditioning
        self.mileage_km = 0.0

    def can_carry(self, passengers: int) -> bool:
        return passengers <= self.capacity

    def register_trip(self, distance_km: float) -> float:
        self.mileage_km += distance_km
        return self.mileage_km


class Transfer:
    """Трансфер (например, аэропорт — отель)."""

    def __init__(self, route: tuple[Address, Address], pickup_time: datetime, bus: Bus, distance_km: float):
        self.from_address, self.to_address = route
        self.pickup_time = pickup_time
        self.bus = bus
        self.distance_km = distance_km
        self.driver: Optional[Driver] = None
        self.passengers: list[Client] = []
        self.is_completed = False

    def add_passenger(self, client: Client) -> None:
        if not self.bus.can_carry(len(self.passengers) + 1):
            raise CapacityExceededException(f"В автобусе {self.bus.plate_number} нет мест")
        self.passengers.append(client)

    def calculate_cost(self) -> float:
        return TRANSFER_BASE_COST + self.distance_km * TRANSFER_COST_PER_KM

    def estimate_arrival(self) -> datetime:
        return self.pickup_time + timedelta(hours=self.distance_km / AVERAGE_BUS_SPEED_KMH)

    def complete(self) -> None:
        if self.driver is None or self.is_completed:
            raise InvalidBookingStateException("Трансфер без водителя или уже завершён")
        self.bus.register_trip(self.distance_km)
        self.is_completed = True
