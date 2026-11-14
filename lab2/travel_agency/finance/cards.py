"""Банковские карты, платежи, платёжный процессор и возвраты."""
from __future__ import annotations

import hashlib
from datetime import date
from typing import TYPE_CHECKING, Optional

from travel_agency.constants import (
    BASE_CURRENCY,
    CARD_MASK_SYMBOL,
    CARD_NUMBER_LENGTH,
    CARD_VISIBLE_DIGITS,
    DEFAULT_PROCESSOR_COMMISSION_PERCENT,
    PERCENT_BASE,
)
from travel_agency.exceptions import (
    CardExpiredException,
    InsufficientFundsException,
    InvalidBookingStateException,
    InvalidPaymentDataException,
    RefundNotAllowedException,
)
from travel_agency.statuses import PaymentStatus, RefundStatus

if TYPE_CHECKING:
    from travel_agency.booking.booking import Booking
    from travel_agency.people.staff import Manager


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


class BankCard:
    """Банковская карта. Полный номер и CVV не хранятся — только маска и хеш."""

    def __init__(self, card_number: str, holder_name: str, expiry_date: date, cvv: str, balance: float = 0.0):
        if not card_number.isdigit() or len(card_number) != CARD_NUMBER_LENGTH:
            raise InvalidPaymentDataException(f"Номер карты должен состоять из {CARD_NUMBER_LENGTH} цифр")
        hidden_part = CARD_MASK_SYMBOL * (CARD_NUMBER_LENGTH - CARD_VISIBLE_DIGITS)
        self.masked_number = hidden_part + card_number[-CARD_VISIBLE_DIGITS:]
        self.holder_name = holder_name
        self.expiry_date = expiry_date
        self.cvv_hash = hash_secret(cvv)
        self.balance = balance

    @staticmethod
    def _validate_amount(amount: float) -> None:
        if amount <= 0:
            raise InvalidPaymentDataException(f"Сумма должна быть положительной: {amount}")

    def is_expired(self, day: date) -> bool:
        return day > self.expiry_date

    def verify_cvv(self, cvv: str) -> bool:
        return hash_secret(cvv) == self.cvv_hash

    def withdraw(self, amount: float, day: date) -> float:
        self._validate_amount(amount)
        if self.is_expired(day):
            raise CardExpiredException(f"Карта {self.masked_number} просрочена")
        if amount > self.balance:
            raise InsufficientFundsException(f"На карте {self.masked_number} недостаточно средств")
        self.balance -= amount
        return self.balance

    def deposit(self, amount: float) -> float:
        self._validate_amount(amount)
        self.balance += amount
        return self.balance


class Payment:
    """Платёж по бронированию."""

    def __init__(self, payment_id: str, amount: float, card: BankCard, booking: Optional[Booking], created_at: date):
        self.payment_id = payment_id
        self.amount = amount
        self.currency = BASE_CURRENCY
        self.card = card
        self.booking = booking
        self.created_at = created_at
        self.status = PaymentStatus.PENDING
        self.refunded_amount = 0.0

    def process(self) -> None:
        if self.status is not PaymentStatus.PENDING:
            raise InvalidBookingStateException(f"Платёж {self.payment_id} уже обработан")
        self.card.withdraw(self.amount, self.created_at)
        self.status = PaymentStatus.COMPLETED

    def refund(self, amount: float) -> None:
        if self.status is not PaymentStatus.COMPLETED:
            raise RefundNotAllowedException(f"Платёж {self.payment_id} нельзя вернуть")
        if not 0 <= amount <= self.amount:
            raise InvalidPaymentDataException(f"Некорректная сумма возврата: {amount}")
        if amount > 0:
            self.card.deposit(amount)
        self.refunded_amount = amount
        self.status = PaymentStatus.REFUNDED


class PaymentProcessor:
    """Проводит списания, переводы между картами и откаты."""

    def __init__(self, commission_percent: float = DEFAULT_PROCESSOR_COMMISSION_PERCENT):
        self.commission_percent = commission_percent
        self.transaction_log: list[Payment] = []

    def _next_payment_id(self) -> str:
        return f"P{len(self.transaction_log) + 1:05d}"

    def calculate_commission(self, amount: float) -> float:
        return round(amount * self.commission_percent / PERCENT_BASE, 2)

    def charge(self, card: BankCard, amount: float, booking: Optional[Booking], day: date) -> Payment:
        payment = Payment(self._next_payment_id(), amount, card, booking, day)
        payment.process()
        self.transaction_log.append(payment)
        return payment

    def transfer(self, source: BankCard, target: BankCard, amount: float, day: date) -> float:
        """Перевод с карты на карту; комиссия списывается с отправителя."""
        commission = self.calculate_commission(amount)
        self.charge(source, amount + commission, None, day)
        target.deposit(amount)
        return commission

    def rollback(self, payment: Payment) -> None:
        payment.refund(payment.amount)


class Refund:
    """Заявка на возврат средств, требующая одобрения менеджера."""

    def __init__(self, payment: Payment, amount: float, reason: str):
        if not 0 < amount <= payment.amount:
            raise InvalidPaymentDataException(f"Сумма возврата {amount} некорректна")
        self.payment = payment
        self.amount = amount
        self.reason = reason
        self.status = RefundStatus.PENDING
        self.approved_by: Optional[Manager] = None

    def _require_pending(self) -> None:
        if self.status is not RefundStatus.PENDING:
            raise RefundNotAllowedException(f"Заявка уже рассмотрена: {self.status.value}")

    def approve(self, manager: Manager) -> None:
        self._require_pending()
        self.approved_by = manager
        self.status = RefundStatus.APPROVED

    def reject(self) -> None:
        self._require_pending()
        self.status = RefundStatus.REJECTED

    def execute(self) -> None:
        if self.status is not RefundStatus.APPROVED:
            raise RefundNotAllowedException("Выполнить можно только одобренный возврат")
        self.payment.refund(self.amount)
        self.status = RefundStatus.EXECUTED
