"""Сервис бронирования: связывает бронь, оплату и уведомления."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from travel_agency.booking.booking import Booking, Cancellation
from travel_agency.exceptions import BookingNotFoundException, InvalidBookingStateException, TravelAgencyException

if TYPE_CHECKING:
    from travel_agency.finance.cards import BankCard, Payment, PaymentProcessor
    from travel_agency.people.person import Client
    from travel_agency.service.notifications import NotificationService
    from travel_agency.tours.pricing import TourPackage


class BookingService:
    """Оформление, оплата и отмена бронирований."""

    def __init__(self, processor: PaymentProcessor, notifier: NotificationService):
        self.processor = processor
        self.notifier = notifier
        self.bookings: dict[str, Booking] = {}
        self.payments: dict[str, Payment] = {}

    def create_booking(self, client: Client, package: TourPackage, today: date) -> Booking:
        client.check_travel_documents(package.destination_country(), package.end_date)
        if not package.tour.has_free_places(package.travelers_count):
            raise InvalidBookingStateException(f"В туре «{package.tour.name}» недостаточно мест")
        booking = Booking(f"B{len(self.bookings) + 1:04d}", client, package, today)
        booking.calculate_total()
        self.bookings[booking.booking_id] = booking
        client.add_booking(booking)
        return booking

    def find_booking(self, booking_id: str) -> Booking:
        if booking_id not in self.bookings:
            raise BookingNotFoundException(f"Бронирование {booking_id} не найдено")
        return self.bookings[booking_id]

    def find_by_client(self, client: Client) -> list[Booking]:
        return [booking for booking in self.bookings.values() if booking.client is client]

    def pay_booking(self, booking_id: str, card: BankCard, today: date) -> Payment:
        booking = self.find_booking(booking_id)
        if booking_id in self.payments:
            raise InvalidBookingStateException(f"Бронь {booking_id} уже оплачена")
        payment = self.processor.charge(card, booking.total_price, booking, today)
        try:
            booking.confirm()
        except TravelAgencyException:
            self.processor.rollback(payment)
            raise
        self.payments[booking_id] = payment
        self._reward_loyalty(booking.client, booking.total_price)
        self.notifier.notify_booking_confirmed(booking)
        return payment

    def cancel_booking(self, booking_id: str, reason: str, today: date) -> Cancellation:
        booking = self.find_booking(booking_id)
        cancellation = booking.cancel(reason, today)
        payment = self.payments.get(booking_id)
        if payment is not None:
            refund_amount = cancellation.calculate_refund_amount(payment.amount)
            payment.refund(refund_amount)
        self.notifier.notify_booking_cancelled(booking, cancellation.penalty_amount)
        return cancellation

    @staticmethod
    def _reward_loyalty(client: Client, amount: float) -> Optional[int]:
        if client.loyalty_card is None:
            return None
        return client.loyalty_card.add_points(amount)
