"""Программа лояльности, отзывы и жалобы клиентов."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from travel_agency.constants import (
    FORBIDDEN_REVIEW_WORDS,
    LOYALTY_MULTIPLIERS,
    LOYALTY_TIERS,
    MAX_COMPLAINT_ESCALATION_LEVEL,
    MAX_REVIEW_RATING,
    MIN_REVIEW_RATING,
    POINT_VALUE,
    POINTS_PER_CURRENCY_UNIT,
    POSITIVE_REVIEW_THRESHOLD,
)
from travel_agency.exceptions import InsufficientFundsException, InvalidBookingStateException, InvalidClientDataException
from travel_agency.statuses import ComplaintStatus

if TYPE_CHECKING:
    from travel_agency.booking.booking import Booking
    from travel_agency.people.person import Client
    from travel_agency.tours.tour import Tour


class LoyaltyCard:
    """Бонусная карта: баллы за покупки и уровни привилегий."""

    def __init__(self, card_number: str):
        self.card_number = card_number
        self.points = 0
        self.lifetime_points = 0
        self.tier = LOYALTY_TIERS[-1][0]

    def add_points(self, purchase_amount: float) -> int:
        earned = int(purchase_amount * POINTS_PER_CURRENCY_UNIT * LOYALTY_MULTIPLIERS[self.tier])
        self.points += earned
        self.lifetime_points += earned
        self.upgrade_tier()
        return earned

    def redeem_points(self, points: int) -> float:
        """Списывает баллы и возвращает их денежный эквивалент."""
        if points <= 0 or points > self.points:
            raise InsufficientFundsException(f"Недостаточно баллов: доступно {self.points}")
        self.points -= points
        return points * POINT_VALUE

    def upgrade_tier(self) -> str:
        for tier_name, threshold in LOYALTY_TIERS:
            if self.lifetime_points >= threshold:
                self.tier = tier_name
                break
        return self.tier


class Review:
    """Отзыв клиента о туре."""

    def __init__(self, author: Client, tour: Tour, rating: int, text: str, created_at: date):
        self.author = author
        self.tour = tour
        self.rating = rating
        self.text = text
        self.created_at = created_at
        self.validate()

    def contains_forbidden_words(self) -> bool:
        lowered = self.text.lower()
        return any(word in lowered for word in FORBIDDEN_REVIEW_WORDS)

    def validate(self) -> None:
        if not MIN_REVIEW_RATING <= self.rating <= MAX_REVIEW_RATING:
            raise InvalidClientDataException(f"Оценка должна быть от {MIN_REVIEW_RATING} до {MAX_REVIEW_RATING}")
        if self.contains_forbidden_words():
            raise InvalidClientDataException("Отзыв содержит запрещённые слова")

    def is_positive(self) -> bool:
        return self.rating >= POSITIVE_REVIEW_THRESHOLD


class Complaint:
    """Жалоба клиента по бронированию."""

    def __init__(self, client: Client, booking: Booking, description: str):
        self.client = client
        self.booking = booking
        self.description = description
        self.status = ComplaintStatus.OPEN
        self.escalation_level = 0
        self.resolution: Optional[str] = None

    def escalate(self) -> int:
        if self.status is ComplaintStatus.RESOLVED:
            raise InvalidBookingStateException("Решённую жалобу нельзя эскалировать")
        if self.escalation_level >= MAX_COMPLAINT_ESCALATION_LEVEL:
            raise InvalidBookingStateException("Достигнут максимальный уровень эскалации")
        self.escalation_level += 1
        self.status = ComplaintStatus.ESCALATED
        return self.escalation_level

    def resolve(self, resolution: str) -> None:
        if self.status is ComplaintStatus.RESOLVED:
            raise InvalidBookingStateException("Жалоба уже решена")
        self.resolution = resolution
        self.status = ComplaintStatus.RESOLVED
