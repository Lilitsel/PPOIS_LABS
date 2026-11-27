"""Уведомления клиентов."""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from travel_agency.constants import DEPARTURE_REMINDER_DAYS

if TYPE_CHECKING:
    from travel_agency.booking.booking import Booking
    from travel_agency.people.person import Client

TEMPLATES = {
    "confirmed": "Бронь {booking_id} подтверждена. Сумма: {amount:.2f}",
    "cancelled": "Бронь {booking_id} отменена. Штраф: {penalty:.2f}",
    "reminder": "До вылета по брони {booking_id} осталось дней: {days}",
}


class Notification:
    """Сообщение клиенту по выбранному каналу."""

    def __init__(self, recipient: Client, message: str, channel: str):
        self.recipient = recipient
        self.message = message
        self.channel = channel
        self.sent_at: Optional[datetime] = None

    def mark_as_sent(self, sent_at: datetime) -> None:
        self.sent_at = sent_at

    def is_sent(self) -> bool:
        return self.sent_at is not None


class NotificationService:
    """Формирует и «отправляет» уведомления по шаблонам."""

    def __init__(self, default_channel: str = "email"):
        self.default_channel = default_channel
        self.sent_notifications: list[Notification] = []

    def send(self, recipient: Client, message: str) -> Notification:
        notification = Notification(recipient, message, self.default_channel)
        notification.mark_as_sent(datetime.now())
        self.sent_notifications.append(notification)
        return notification

    def notify_booking_confirmed(self, booking: Booking) -> Notification:
        message = TEMPLATES["confirmed"].format(booking_id=booking.booking_id, amount=booking.total_price)
        return self.send(booking.client, message)

    def notify_booking_cancelled(self, booking: Booking, penalty: float) -> Notification:
        message = TEMPLATES["cancelled"].format(booking_id=booking.booking_id, penalty=penalty)
        return self.send(booking.client, message)

    def notify_departure_reminder(self, booking: Booking, today: date) -> Optional[Notification]:
        days_left = (booking.departure_date - today).days
        if not 0 <= days_left <= DEPARTURE_REMINDER_DAYS:
            return None
        message = TEMPLATES["reminder"].format(booking_id=booking.booking_id, days=days_left)
        return self.send(booking.client, message)

    def send_bulk(self, recipients: list[Client], message: str) -> int:
        for recipient in recipients:
            self.send(recipient, message)
        return len(recipients)

    def history_for(self, client: Client) -> list[Notification]:
        return [notification for notification in self.sent_notifications if notification.recipient is client]
