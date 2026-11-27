"""Документы, удостоверяющие личность и право въезда."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from travel_agency.constants import AVERAGE_DAYS_IN_MONTH, MIN_PASSPORT_VALIDITY_MONTHS
from travel_agency.exceptions import InvalidDateRangeException, VisaRequiredException

if TYPE_CHECKING:
    from travel_agency.geography.places import Country


def ensure_date_order(start: date, end: date) -> None:
    if end < start:
        raise InvalidDateRangeException(f"Дата {end} раньше даты {start}")


class Passport:
    """Заграничный паспорт."""

    def __init__(self, number: str, issuing_country: Country, issue_date: date, expiry_date: date):
        ensure_date_order(issue_date, expiry_date)
        self.number = number
        self.issuing_country = issuing_country
        self.issue_date = issue_date
        self.expiry_date = expiry_date

    def is_valid_on(self, day: date) -> bool:
        return self.issue_date <= day <= self.expiry_date

    def months_until_expiry(self, day: date) -> int:
        return (self.expiry_date - day).days // AVERAGE_DAYS_IN_MONTH

    def is_valid_for_trip(self, return_date: date) -> bool:
        """Паспорт должен действовать ещё несколько месяцев после возвращения."""
        return self.is_valid_on(return_date) and self.months_until_expiry(return_date) >= MIN_PASSPORT_VALIDITY_MONTHS


class Visa:
    """Въездная виза в конкретную страну."""

    def __init__(self, visa_type: str, country: Country, valid_from: date, valid_to: date, entries_allowed: int):
        ensure_date_order(valid_from, valid_to)
        self.visa_type = visa_type
        self.country = country
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.entries_allowed = entries_allowed
        self.entries_used = 0

    def covers_date(self, day: date) -> bool:
        return self.valid_from <= day <= self.valid_to

    def has_entries_left(self) -> bool:
        return self.entries_used < self.entries_allowed

    def allows_stay_in(self, country: Country, day: date) -> bool:
        return self.country is country and self.covers_date(day) and self.has_entries_left()

    def register_entry(self, day: date) -> int:
        if not self.covers_date(day):
            raise VisaRequiredException(f"Виза не действует на дату {day}")
        if not self.has_entries_left():
            raise VisaRequiredException("Лимит въездов по визе исчерпан")
        self.entries_used += 1
        return self.entries_allowed - self.entries_used
