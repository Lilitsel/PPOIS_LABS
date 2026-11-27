import unittest
from datetime import date
from tests.factories import CVV, TODAY, make_card, make_person
from travel_agency.exceptions import (
    CardExpiredException,
    InsufficientFundsException,
    InvalidBookingStateException,
    InvalidPaymentDataException,
    RefundNotAllowedException,
)
from travel_agency.finance.cards import BankCard, PaymentProcessor, Refund
from travel_agency.people.staff import Manager
from travel_agency.statuses import PaymentStatus, RefundStatus


class CardsTest(unittest.TestCase):
    def test_card(self):
        card = make_card(balance=100.0)
        self.assertEqual(card.masked_number, "************1111")
        self.assertTrue(card.verify_cvv(CVV))
        self.assertFalse(card.verify_cvv("999"))
        self.assertEqual(card.withdraw(40.0, TODAY), 60.0)
        self.assertEqual(card.deposit(10.0), 70.0)
        with self.assertRaises(InsufficientFundsException):
            card.withdraw(1000.0, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            card.deposit(0)
        with self.assertRaises(CardExpiredException):
            make_card(expiry=date(2025, 1, 1)).withdraw(1.0, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            BankCard("1234", "X", TODAY, CVV)

    def test_processor(self):
        processor = PaymentProcessor()
        source, target = make_card(balance=1000.0), make_card(balance=0.0)
        self.assertEqual(processor.transfer(source, target, 500.0, TODAY), 5.0)
        self.assertEqual(source.balance, 495.0)
        self.assertEqual(target.balance, 500.0)
        payment = processor.charge(source, 100.0, None, TODAY)
        self.assertEqual(payment.payment_id, "P00002")
        with self.assertRaises(InvalidBookingStateException):
            payment.process()
        processor.rollback(payment)
        self.assertEqual(source.balance, 495.0)
        with self.assertRaises(RefundNotAllowedException):
            payment.refund(1.0)

    def test_payment_refund_validation(self):
        payment = PaymentProcessor().charge(make_card(), 100.0, None, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            payment.refund(200.0)
        payment.refund(0.0)
        self.assertIs(payment.status, PaymentStatus.REFUNDED)

    def test_refund_request(self):
        payment = PaymentProcessor().charge(make_card(), 100.0, None, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            Refund(payment, 500.0, "много")
        refund = Refund(payment, 30.0, "частично")
        with self.assertRaises(RefundNotAllowedException):
            refund.execute()
        refund.reject()
        self.assertIs(refund.status, RefundStatus.REJECTED)
        with self.assertRaises(RefundNotAllowedException):
            refund.approve(Manager("M", make_person(), 1.0, TODAY))


if __name__ == "__main__":
    unittest.main()
