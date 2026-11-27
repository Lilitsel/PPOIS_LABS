"""Базовый класс человека и клиент компании."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from travel_agency.constants import ADULT_AGE, EMAIL_SEPARATOR
from travel_agency.exceptions import (
    InvalidClientDataException,
    PassportExpiredException,
    TravelAgencyException,
    VisaRequiredException,
)

if TYPE_CHECKING:
    from travel_agency.booking.booking import Booking
    from travel_agency.documents.identity import Passport, Visa
    from travel_agency.finance.cards import BankCard
    from travel_agency.geography.places import Country
    from travel_agency.service.clients import LoyaltyCard


class Person:
    """Человек с контактными данными."""

    def __init__(self, first_name: str, last_name: str, birth_date: date, phone: str, email: str):
        if not first_name.strip() or not last_name.strip():
            raise InvalidClientDataException("Имя и фамилия не могут быть пустыми")
        if EMAIL_SEPARATOR not in email:
            raise InvalidClientDataException(f"Некорректный email: {email}")
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.phone = phone
        self.email = email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def calculate_age(self, on_date: Optional[date] = None) -> int:
        on_date = on_date or date.today()
        had_birthday = (on_date.month, on_date.day) >= (self.birth_date.month, self.birth_date.day)
        years = on_date.year - self.birth_date.year
        return years if had_birthday else years - 1

    def is_adult(self, on_date: Optional[date] = None) -> bool:
        return self.calculate_age(on_date) >= ADULT_AGE


class Client(Person):
    """Клиент туристической компании."""

    def __init__(self, client_id: str, first_name: str, last_name: str, birth_date: date, phone: str, email: str):
        super().__init__(first_name, last_name, birth_date, phone, email)
        self.client_id = client_id
        self.passport: Optional[Passport] = None
        self.visas: list[Visa] = []
        self.loyalty_card: Optional[LoyaltyCard] = None
        self.bank_card: Optional[BankCard] = None
        self.bookings: list[Booking] = []

    def add_visa(self, visa: Visa) -> None:
        self.visas.append(visa)

    def add_booking(self, booking: Booking) -> None:
        if booking not in self.bookings:
            self.bookings.append(booking)

    def get_active_bookings(self) -> list[Booking]:
        return [booking for booking in self.bookings if booking.is_active()]

    def check_travel_documents(self, country: Country, return_date: date) -> None:
        """Проверяет паспорт и визу для поездки; бросает исключение при проблеме."""
        if self.passport is None:
            raise InvalidClientDataException(f"У клиента {self.full_name} нет паспорта")
        if not self.passport.is_valid_for_trip(return_date):
            raise PassportExpiredException(f"Паспорт {self.passport.number} истекает слишком рано")
        if not country.requires_visa_for(self.passport):
            return
        if not any(visa.allows_stay_in(country, return_date) for visa in self.visas):
            raise VisaRequiredException(f"Для поездки в страну «{country.name}» нужна виза")

    def can_travel_to(self, country: Country, return_date: date) -> bool:
        try:
            self.check_travel_documents(country, return_date)
        except TravelAgencyException:
            return False
        return True
