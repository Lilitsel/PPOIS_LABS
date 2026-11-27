"""Скидки, промокоды и сборка туристического пакета."""
from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING, Optional

from travel_agency.constants import PERCENT_BASE
from travel_agency.exceptions import InvalidPromoCodeException, InvalidTourDataException

if TYPE_CHECKING:
    from travel_agency.accommodation.hotel import HotelReservation
    from travel_agency.documents.papers import InsurancePolicy
    from travel_agency.geography.places import Country
    from travel_agency.tours.tour import Tour
    from travel_agency.transport.air import Flight
    from travel_agency.transport.ground import Transfer


class Discount:
    """Процентная скидка с порогом суммы и сроком действия."""

    def __init__(self, name: str, percent: float, valid_until: date, min_order_amount: float = 0.0):
        if not 0 < percent < PERCENT_BASE:
            raise InvalidPromoCodeException(f"Некорректный процент скидки: {percent}")
        self.name = name
        self.percent = percent
        self.valid_until = valid_until
        self.min_order_amount = min_order_amount
        self.is_approved = False

    def is_applicable(self, amount: float, day: date) -> bool:
        return self.is_approved and day <= self.valid_until and amount >= self.min_order_amount

    def apply(self, amount: float, day: date) -> float:
        if not self.is_applicable(amount, day):
            return amount
        return amount * (PERCENT_BASE - self.percent) / PERCENT_BASE


class PromoCode:
    """Промокод с ограниченным числом использований."""

    def __init__(self, code: str, discount: Discount, usage_limit: int):
        self.code = code.upper()
        self.discount = discount
        self.usage_limit = usage_limit
        self.times_used = 0

    def is_exhausted(self) -> bool:
        return self.times_used >= self.usage_limit

    def redeem(self, amount: float, day: date) -> float:
        if self.is_exhausted() or not self.discount.is_applicable(amount, day):
            raise InvalidPromoCodeException(f"Промокод {self.code} нельзя применить")
        self.times_used += 1
        return self.discount.apply(amount, day)


class TourPackage:
    """Пакет: тур + проживание + перелёт + трансфер + страховки."""

    def __init__(self, tour: Tour, start_date: date, travelers_count: int):
        if travelers_count <= 0:
            raise InvalidTourDataException("Количество путешественников должно быть положительным")
        self.tour = tour
        self.start_date = start_date
        self.travelers_count = travelers_count
        self.hotel_reservation: Optional[HotelReservation] = None
        self.flight: Optional[Flight] = None
        self.transfer: Optional[Transfer] = None
        self.insurances: list[InsurancePolicy] = []
        self.discount: Optional[Discount] = None

    @property
    def end_date(self) -> date:
        return self.start_date + timedelta(days=self.tour.duration_days)

    def destination_country(self) -> Country:
        return self.tour.destination.country

    def apply_discount(self, discount: Discount) -> None:
        self.discount = discount

    def validate_completeness(self) -> None:
        if self.tour.duration_days > 1 and self.hotel_reservation is None:
            raise InvalidTourDataException("Для многодневного тура нужно проживание")
        if self.hotel_reservation is not None and self.hotel_reservation.guests < self.travelers_count:
            raise InvalidTourDataException("Номер рассчитан на меньшее число гостей")

    def _components_cost(self) -> float:
        cost = self.tour.calculate_price_for_group(self.travelers_count, self.start_date)
        if self.hotel_reservation is not None:
            cost += self.hotel_reservation.calculate_total()
        if self.flight is not None:
            cost += self.flight.base_price * self.travelers_count
        if self.transfer is not None:
            cost += self.transfer.calculate_cost()
        return cost + sum(policy.calculate_premium() for policy in self.insurances)

    def calculate_total_price(self, day: Optional[date] = None) -> float:
        total = self._components_cost()
        if self.discount is not None:
            total = self.discount.apply(total, day or date.today())
        return round(total, 2)
