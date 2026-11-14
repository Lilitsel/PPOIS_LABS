"""Правила расчёта штрафа при отмене."""
from travel_agency.constants import CANCELLATION_PENALTY_RULES, PERCENT_BASE


class CancellationPolicy:
    """Штраф зависит от того, за сколько дней до вылета отменена поездка."""

    def __init__(self, rules: tuple[tuple[int, int], ...] = CANCELLATION_PENALTY_RULES):
        self.rules = sorted(rules, reverse=True)

    def penalty_percent_for(self, days_before: int) -> int:
        for min_days, percent in self.rules:
            if days_before >= min_days:
                return percent
        return PERCENT_BASE

    def calculate_penalty(self, amount: float, days_before: int) -> float:
        return round(amount * self.penalty_percent_for(days_before) / PERCENT_BASE, 2)
