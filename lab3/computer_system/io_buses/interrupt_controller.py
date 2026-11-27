from computer_system.exceptions.interrupt_failure_exception import InterruptFailureException


class InterruptController:
    def __init__(self, max_irq_lines: int = 256):
        self.max_irq_lines = max_irq_lines
        self.pending_irqs: list[int] = []
        self.handled_count: int = 0

    def raise_irq(self, irq_number: int) -> int:
        if not (0 <= irq_number < self.max_irq_lines):
            raise InterruptFailureException("Invalid IRQ line number")
        self.pending_irqs.append(irq_number)
        return len(self.pending_irqs)

    def handle_next_irq(self) -> int | None:
        if not self.pending_irqs:
            return None
        irq = self.pending_irqs.pop(0)
        self.handled_count += 1
        return irq
