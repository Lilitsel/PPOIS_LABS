"""Туристическая компания и её филиалы."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from travel_agency.booking.service import BookingService
from travel_agency.exceptions import (
    EmployeeNotFoundException,
    InvalidClientDataException,
    InvalidTourDataException,
    RoomNotAvailableException,
    TravelAgencyException,
)
from travel_agency.tours.pricing import TourPackage

if TYPE_CHECKING:
    from travel_agency.accommodation.hotel import Hotel
    from travel_agency.booking.booking import Booking
    from travel_agency.geography.places import Address, City, Country
    from travel_agency.people.person import Client
    from travel_agency.people.staff import Employee
    from travel_agency.tours.tour import Tour
    from travel_agency.transport.air import Flight


class Branch:
    """Офис продаж компании."""

    def __init__(self, name: str, address: Address, opening_hour: int, closing_hour: int):
        self.name = name
        self.address = address
        self.opening_hour = opening_hour
        self.closing_hour = closing_hour
        self.employees: dict[str, Employee] = {}

    def hire_employee(self, employee: Employee) -> None:
        if employee.employee_id in self.employees:
            raise InvalidClientDataException(f"Сотрудник {employee.employee_id} уже работает в филиале")
        employee.branch = self
        self.employees[employee.employee_id] = employee

    def fire_employee(self, employee_id: str) -> Employee:
        if employee_id not in self.employees:
            raise EmployeeNotFoundException(f"Сотрудник {employee_id} не найден в филиале {self.name}")
        employee = self.employees.pop(employee_id)
        employee.branch = None
        return employee

    def is_open_at(self, hour: int) -> bool:
        return self.opening_hour <= hour < self.closing_hour

    def calculate_payroll(self) -> float:
        return sum(employee.salary for employee in self.employees.values())


class TravelCompany:
    """Корневой объект предметной области: туры, клиенты, партнёры, продажи."""

    def __init__(self, name: str, license_number: str, booking_service: BookingService, home_country: Country):
        self.name = name
        self.home_country = home_country
        self.license_number = license_number
        self.booking_service = booking_service
        self.branches: list[Branch] = []
        self.tours: dict[str, Tour] = {}
        self.clients: dict[str, Client] = {}
        self.hotels: list[Hotel] = []
        self.flights: list[Flight] = []

    def open_branch(self, branch: Branch) -> None:
        self.branches.append(branch)

    def add_partner_hotel(self, hotel: Hotel) -> None:
        self.hotels.append(hotel)

    def add_flight(self, flight: Flight) -> None:
        self.flights.append(flight)

    def register_client(self, client: Client) -> None:
        if client.client_id in self.clients:
            raise InvalidClientDataException(f"Клиент с номером {client.client_id} уже зарегистрирован")
        self.clients[client.client_id] = client

    def find_client(self, client_id: str) -> Client:
        if client_id not in self.clients:
            raise InvalidClientDataException(f"Клиент {client_id} не найден")
        return self.clients[client_id]

    def add_tour(self, tour: Tour) -> None:
        if tour.tour_id in self.tours:
            raise InvalidTourDataException(f"Тур {tour.tour_id} уже существует")
        self.tours[tour.tour_id] = tour

    def find_tour(self, tour_id: str) -> Tour:
        if tour_id not in self.tours:
            raise InvalidTourDataException(f"Тур {tour_id} не найден")
        return self.tours[tour_id]

    def search_tours(self, max_price: Optional[float] = None, month: Optional[int] = None) -> list[Tour]:
        return [tour for tour in self.tours.values() if self._matches(tour, max_price, month)]

    @staticmethod
    def _matches(tour: Tour, max_price: Optional[float], month: Optional[int]) -> bool:
        price_ok = max_price is None or tour.base_price <= max_price
        month_ok = month is None or tour.destination.is_recommended_in_month(month)
        return price_ok and month_ok and tour.has_free_places()

    def find_hotel_in_city(self, city: City) -> Hotel:
        for hotel in self.hotels:
            if hotel.address.city is city:
                return hotel
        raise RoomNotAvailableException(f"В городе {city.name} нет отелей-партнёров")

    def find_flight_to(self, city: City, day: date) -> Optional[Flight]:
        for flight in self.flights:
            if flight.flies_to(city) and flight.departure_time.date() == day:
                return flight
        return None

    def assemble_package(self, client: Client, tour: Tour, start_date: date, travelers: int) -> TourPackage:
        """Собирает пакет: тур + номер в отеле-партнёре + рейс, если он есть на эту дату."""
        package = TourPackage(tour, start_date, travelers)
        city = tour.destination.city
        hotel = self.find_hotel_in_city(city)
        package.hotel_reservation = hotel.reserve_room(client, travelers, start_date, package.end_date)
        package.flight = self.find_flight_to(city, start_date)
        return package

    def book_tour(self, client_id: str, tour_id: str, trip: tuple[date, int], today: date) -> Booking:
        """trip — дата начала и число путешественников. При ошибке бронь отеля снимается."""
        start_date, travelers = trip
        client = self.find_client(client_id)
        package = self.assemble_package(client, self.find_tour(tour_id), start_date, travelers)
        try:
            return self.booking_service.create_booking(client, package, today)
        except TravelAgencyException:
            package.hotel_reservation.cancel()
            raise

    def all_bookings(self) -> list[Booking]:
        return list(self.booking_service.bookings.values())
