"""Бронирование тура, отмена и лист ожидания."""
from __future__ import annotations

from collections import deque
from datetime import date
from typing import TYPE_CHECKING, Optional

from travel_agency.booking.policy import CancellationPolicy
from travel_agency.exceptions import CapacityExceededException, InvalidBookingStateException
from travel_agency.statuses import BookingStatus

if TYPE_CHECKING:
    from travel_agency.people.person import Client, Person
    from travel_agency.tours.pricing import TourPackage
    from travel_agency.tours.tour import Tour


class Booking:
    """Бронирование туристического пакета клиентом."""

    def __init__(self, booking_id: str, client: Client, package: TourPackage, created_at: date):
        self.booking_id = booking_id
        self.client = client
        self.package = package
        self.created_at = created_at
        self.travelers: list[Person] = [client]
        self.status = BookingStatus.PENDING
        self.total_price = 0.0

    @property
    def departure_date(self) -> date:
        return self.package.start_date

    def destination_name(self) -> str:
        tour = self.package.tour
        return tour.destination_name

    def is_active(self) -> bool:
        return self.status in (BookingStatus.PENDING, BookingStatus.CONFIRMED)

    def _require_status(self, expected: BookingStatus) -> None:
        if self.status is not expected:
            raise InvalidBookingStateException(f"Бронь {self.booking_id} в статусе «{self.status.value}»")

    def add_traveler(self, person: Person) -> None:
        self._require_status(BookingStatus.PENDING)
        if len(self.travelers) >= self.package.travelers_count:
            raise CapacityExceededException("Все места в пакете уже распределены")
        self.travelers.append(person)

    def calculate_total(self) -> float:
        self.total_price = self.package.calculate_total_price(self.created_at)
        return self.total_price

    def confirm(self) -> None:
        self._require_status(BookingStatus.PENDING)
        self.package.validate_completeness()
        tour = self.package.tour
        tour.reserve_places(self.package.travelers_count)
        self.status = BookingStatus.CONFIRMED

    def cancel(self, reason: str, cancel_date: date) -> Cancellation:
        if not self.is_active():
            raise InvalidBookingStateException(f"Бронь {self.booking_id} нельзя отменить")
        if self.status is BookingStatus.CONFIRMED:
            tour = self.package.tour
            tour.release_places(self.package.travelers_count)
        reservation = self.package.hotel_reservation
        if reservation is not None and not reservation.is_cancelled:
            reservation.cancel()
        self.status = BookingStatus.CANCELLED
        return Cancellation(self, reason, cancel_date)

    def complete(self) -> None:
        self._require_status(BookingStatus.CONFIRMED)
        self.status = BookingStatus.COMPLETED


class Cancellation:
    """Факт отмены бронирования со штрафом."""

    def __init__(self, booking: Booking, reason: str, cancel_date: date, policy: Optional[CancellationPolicy] = None):
        self.booking = booking
        self.reason = reason
        self.cancel_date = cancel_date
        self.policy = policy or CancellationPolicy()
        self.penalty_amount = self.calculate_penalty()

    def days_before_departure(self) -> int:
        return (self.booking.departure_date - self.cancel_date).days

    def calculate_penalty(self) -> float:
        return self.policy.calculate_penalty(self.booking.total_price, self.days_before_departure())

    def calculate_refund_amount(self, paid_amount: float) -> float:
        return max(0.0, round(paid_amount - self.penalty_amount, 2))


class Waitlist:
    """Очередь клиентов, ожидающих место в туре."""

    def __init__(self, tour: Tour, max_size: int):
        self.tour = tour
        self.max_size = max_size
        self.queue: deque[Client] = deque()

    def enqueue(self, client: Client) -> int:
        if client in self.queue:
            return self.position_of(client)
        if len(self.queue) >= self.max_size:
            raise CapacityExceededException("Лист ожидания заполнен")
        self.queue.append(client)
        return len(self.queue)

    def position_of(self, client: Client) -> int:
        """Позиция клиента в очереди начиная с 1; 0 — клиента нет в очереди."""
        return list(self.queue).index(client) + 1 if client in self.queue else 0

    def promote_next(self) -> Optional[Client]:
        if not self.queue or not self.tour.has_free_places():
            return None
        return self.queue.popleft()
