"""Договоры, страховые полисы, ваучеры и авиабилеты."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

from travel_agency.booking.policy import CancellationPolicy
from travel_agency.constants import (
    CHECK_IN_CLOSE_HOURS,
    CHECK_IN_OPEN_HOURS,
    DEFAULT_VOUCHER_VALIDITY_DAYS,
    INSURANCE_COVERAGE_RATE,
    INSURANCE_DAILY_RATE,
    SENIOR_AGE,
    SENIOR_INSURANCE_MULTIPLIER,
)
from travel_agency.documents.identity import ensure_date_order
from travel_agency.exceptions import InsuranceClaimRejectedException, InvalidBookingStateException
from travel_agency.statuses import TicketStatus

if TYPE_CHECKING:
    from travel_agency.booking.booking import Booking
    from travel_agency.people.person import Client, Person
    from travel_agency.transport.air import Flight, Seat


class InsurancePolicy:
    """Туристическая медицинская страховка."""

    def __init__(self, policy_number: str, insured_person: Person, start_date: date, end_date: date, coverage_amount: float):
        ensure_date_order(start_date, end_date)
        self.policy_number = policy_number
        self.insured_person = insured_person
        self.start_date = start_date
        self.end_date = end_date
        self.coverage_amount = coverage_amount
        self.claims: list[float] = []

    def calculate_premium(self) -> float:
        days = (self.end_date - self.start_date).days + 1
        premium = days * INSURANCE_DAILY_RATE + self.coverage_amount * INSURANCE_COVERAGE_RATE
        if self.insured_person.calculate_age(self.start_date) >= SENIOR_AGE:
            premium *= SENIOR_INSURANCE_MULTIPLIER
        return round(premium, 2)

    def covers_date(self, day: date) -> bool:
        return self.start_date <= day <= self.end_date

    def remaining_coverage(self) -> float:
        return self.coverage_amount - sum(self.claims)

    def file_claim(self, amount: float, incident_date: date) -> float:
        if not self.covers_date(incident_date):
            raise InsuranceClaimRejectedException(f"Полис не действует на дату {incident_date}")
        if amount > self.remaining_coverage():
            raise InsuranceClaimRejectedException("Сумма превышает остаток страхового покрытия")
        self.claims.append(amount)
        return self.remaining_coverage()


class Contract:
    """Договор на туристическое обслуживание."""

    def __init__(self, contract_number: str, client: Client, booking: Booking, terms: str):
        self.contract_number = contract_number
        self.client = client
        self.booking = booking
        self.terms = terms
        self.sign_date: date | None = None
        self.is_terminated = False

    @property
    def is_signed(self) -> bool:
        return self.sign_date is not None

    def sign(self, day: date) -> None:
        if self.is_signed:
            raise InvalidBookingStateException(f"Договор {self.contract_number} уже подписан")
        self.sign_date = day

    def calculate_penalty(self, day: date) -> float:
        days_before = (self.booking.departure_date - day).days
        return CancellationPolicy().calculate_penalty(self.booking.total_price, days_before)

    def terminate(self, day: date) -> float:
        if not self.is_signed or self.is_terminated:
            raise InvalidBookingStateException("Расторгнуть можно только действующий договор")
        self.is_terminated = True
        return self.calculate_penalty(day)


class Voucher:
    """Туристический ваучер — подтверждение для отеля и принимающей стороны."""

    def __init__(self, code: str, booking: Booking, issue_date: date, valid_days: int = DEFAULT_VOUCHER_VALIDITY_DAYS):
        self.code = code
        self.booking = booking
        self.issue_date = issue_date
        self.valid_days = valid_days
        self.is_used = False

    def is_expired(self, day: date) -> bool:
        return day > self.issue_date + timedelta(days=self.valid_days)

    def redeem(self, day: date) -> None:
        if self.is_used or self.is_expired(day):
            raise InvalidBookingStateException(f"Ваучер {self.code} недействителен")
        self.is_used = True


class Ticket:
    """Авиабилет на конкретное место."""

    def __init__(self, ticket_number: str, passenger: Person, flight: Flight, seat: Seat):
        self.ticket_number = ticket_number
        self.passenger = passenger
        self.flight = flight
        self.seat = seat
        self.price = flight.calculate_seat_price(seat)
        self.status = TicketStatus.ISSUED

    def check_in(self, now: datetime) -> None:
        if self.status is not TicketStatus.ISSUED:
            raise InvalidBookingStateException(f"Регистрация по билету невозможна: {self.status.value}")
        hours_left = (self.flight.departure_time - now).total_seconds() / timedelta(hours=1).total_seconds()
        if not CHECK_IN_CLOSE_HOURS <= hours_left <= CHECK_IN_OPEN_HOURS:
            raise InvalidBookingStateException("Регистрация на рейс сейчас закрыта")
        self.status = TicketStatus.CHECKED_IN

    def cancel(self) -> None:
        if self.status is TicketStatus.CANCELLED:
            raise InvalidBookingStateException("Билет уже аннулирован")
        self.seat.release()
        self.status = TicketStatus.CANCELLED

    def change_seat(self, new_seat_number: str) -> None:
        new_seat = self.flight.book_seat(new_seat_number)
        self.seat.release()
        self.seat = new_seat
        self.price = self.flight.calculate_seat_price(new_seat)
