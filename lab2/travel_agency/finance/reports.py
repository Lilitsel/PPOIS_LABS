"""Счета, конвертация валют и отчёты о продажах."""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import TYPE_CHECKING, Optional

from travel_agency.constants import (
    BASE_CURRENCY,
    DEFAULT_INVOICE_PAYMENT_DAYS,
    DEFAULT_TOP_DESTINATIONS,
    DEFAULT_VAT_PERCENT,
    PERCENT_BASE,
)
from travel_agency.documents.identity import ensure_date_order
from travel_agency.exceptions import InvalidPaymentDataException
from travel_agency.statuses import BookingStatus

if TYPE_CHECKING:
    from travel_agency.booking.booking import Booking


class Invoice:
    """Счёт на оплату с НДС."""

    def __init__(self, invoice_number: str, booking: Booking, issue_date: date, vat_percent: float = DEFAULT_VAT_PERCENT):
        self.invoice_number = invoice_number
        self.booking = booking
        self.issue_date = issue_date
        self.due_date = issue_date + timedelta(days=DEFAULT_INVOICE_PAYMENT_DAYS)
        self.vat_percent = vat_percent
        self.items: list[tuple[str, float]] = []

    def add_item(self, description: str, amount: float) -> None:
        if amount < 0:
            raise InvalidPaymentDataException(f"Сумма позиции не может быть отрицательной: {amount}")
        self.items.append((description, amount))

    def calculate_subtotal(self) -> float:
        return sum(amount for _, amount in self.items)

    def calculate_vat(self) -> float:
        return round(self.calculate_subtotal() * self.vat_percent / PERCENT_BASE, 2)

    def calculate_total(self) -> float:
        return self.calculate_subtotal() + self.calculate_vat()

    def is_overdue(self, day: date, is_paid: bool) -> bool:
        return not is_paid and day > self.due_date


class CurrencyConverter:
    """Конвертация через базовую валюту (курс = единиц валюты за 1 базовую)."""

    def __init__(self, base_currency: str = BASE_CURRENCY):
        self.base_currency = base_currency
        self.rates: dict[str, float] = {base_currency: 1.0}
        self.last_updated: Optional[date] = None

    def update_rate(self, currency: str, rate: float, day: date) -> None:
        if rate <= 0:
            raise InvalidPaymentDataException(f"Курс должен быть положительным: {rate}")
        self.rates[currency.upper()] = rate
        self.last_updated = day

    def _rate_of(self, currency: str) -> float:
        code = currency.upper()
        if code not in self.rates:
            raise InvalidPaymentDataException(f"Неизвестная валюта: {currency}")
        return self.rates[code]

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        amount_in_base = amount / self._rate_of(from_currency)
        return round(amount_in_base * self._rate_of(to_currency), 2)


class SalesReport:
    """Отчёт о продажах за период (учитываются подтверждённые и завершённые брони)."""

    COUNTED_STATUSES = (BookingStatus.CONFIRMED, BookingStatus.COMPLETED)

    def __init__(self, period_start: date, period_end: date, bookings: list[Booking]):
        ensure_date_order(period_start, period_end)
        self.period_start = period_start
        self.period_end = period_end
        self.bookings = [booking for booking in bookings if self._is_counted(booking)]

    def _is_counted(self, booking: Booking) -> bool:
        in_period = self.period_start <= booking.created_at <= self.period_end
        return in_period and booking.status in self.COUNTED_STATUSES

    def calculate_revenue(self) -> float:
        return round(sum(booking.total_price for booking in self.bookings), 2)

    def average_check(self) -> float:
        if not self.bookings:
            return 0.0
        return round(self.calculate_revenue() / len(self.bookings), 2)

    def top_destinations(self, limit: int = DEFAULT_TOP_DESTINATIONS) -> list[tuple[str, int]]:
        city_names = [booking.destination_name() for booking in self.bookings]
        return Counter(city_names).most_common(limit)
