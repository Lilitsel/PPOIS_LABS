"""Авиакомпании, аэропорты, рейсы и места."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from travel_agency.documents.identity import ensure_date_order
from travel_agency.documents.papers import Ticket
from travel_agency.exceptions import InvalidTourDataException, SeatNotAvailableException

if TYPE_CHECKING:
    from travel_agency.geography.places import City
    from travel_agency.people.person import Person


class Airline:
    """Авиакомпания с правилами провоза багажа."""

    def __init__(self, name: str, iata_code: str, baggage_allowance_kg: float, fee_per_extra_kg: float):
        self.name = name
        self.iata_code = iata_code
        self.baggage_allowance_kg = baggage_allowance_kg
        self.fee_per_extra_kg = fee_per_extra_kg

    def calculate_baggage_fee(self, baggage_weight_kg: float) -> float:
        extra_weight = max(0.0, baggage_weight_kg - self.baggage_allowance_kg)
        return extra_weight * self.fee_per_extra_kg


class Airport:
    """Аэропорт в городе."""

    def __init__(self, name: str, iata_code: str, city: City, terminals: set[str]):
        self.name = name
        self.iata_code = iata_code
        self.city = city
        self.terminals = terminals

    def has_terminal(self, terminal: str) -> bool:
        return terminal in self.terminals


class Seat:
    """Место в самолёте."""

    def __init__(self, number: str, seat_class: str, price_multiplier: float):
        self.number = number
        self.seat_class = seat_class
        self.price_multiplier = price_multiplier
        self.is_occupied = False

    def occupy(self) -> None:
        if self.is_occupied:
            raise SeatNotAvailableException(f"Место {self.number} уже занято")
        self.is_occupied = True

    def release(self) -> None:
        self.is_occupied = False


class Flight:
    """Авиарейс между двумя аэропортами."""

    def __init__(self, flight_number: str, airline: Airline, route: tuple[Airport, Airport],
                 schedule: tuple[datetime, datetime], base_price: float):
        departure_time, arrival_time = schedule
        ensure_date_order(departure_time, arrival_time)
        self.flight_number = flight_number
        self.airline = airline
        self.departure_airport, self.arrival_airport = route
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.base_price = base_price
        self.seats: dict[str, Seat] = {}
        self.issued_tickets: list[Ticket] = []

    def add_seat(self, seat: Seat) -> None:
        if seat.number in self.seats:
            raise InvalidTourDataException(f"Место {seat.number} уже добавлено в рейс")
        self.seats[seat.number] = seat

    def calculate_duration(self) -> timedelta:
        return self.arrival_time - self.departure_time

    def find_free_seat(self, seat_class: Optional[str] = None) -> Seat:
        for seat in self.seats.values():
            if not seat.is_occupied and seat_class in (None, seat.seat_class):
                return seat
        raise SeatNotAvailableException(f"На рейсе {self.flight_number} нет свободных мест")

    def book_seat(self, seat_number: str) -> Seat:
        if seat_number not in self.seats:
            raise SeatNotAvailableException(f"Места {seat_number} нет на рейсе {self.flight_number}")
        seat = self.seats[seat_number]
        seat.occupy()
        return seat

    def calculate_seat_price(self, seat: Seat) -> float:
        return self.base_price * seat.price_multiplier

    def issue_ticket(self, passenger: Person, seat_class: Optional[str] = None) -> Ticket:
        seat = self.book_seat(self.find_free_seat(seat_class).number)
        ticket = Ticket(f"{self.flight_number}-{len(self.issued_tickets) + 1}", passenger, self, seat)
        self.issued_tickets.append(ticket)
        return ticket

    def flies_to(self, city: City) -> bool:
        return self.arrival_airport.city is city
