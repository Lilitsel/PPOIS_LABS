import unittest
from datetime import date
from tests.factories import START, TODAY, make_client, make_package
from travel_agency.booking.booking import Booking
from travel_agency.exceptions import InvalidPaymentDataException
from travel_agency.finance.reports import CurrencyConverter, Invoice, SalesReport


class ReportsTest(unittest.TestCase):
    def setUp(self):
        client = make_client()
        self.booking = Booking("B1", client, make_package(client=client), TODAY)
        self.booking.calculate_total()

    def test_invoice(self):
        invoice = Invoice("I1", self.booking, TODAY)
        invoice.add_item("Тур", 1000.0)
        invoice.add_item("Страховка", 50.0)
        self.assertEqual(invoice.calculate_vat(), 210.0)
        self.assertEqual(invoice.calculate_total(), 1260.0)
        self.assertTrue(invoice.is_overdue(date(2026, 4, 1), False))
        self.assertFalse(invoice.is_overdue(date(2026, 4, 1), True))
        with self.assertRaises(InvalidPaymentDataException):
            invoice.add_item("Ошибка", -1.0)

    def test_converter(self):
        converter = CurrencyConverter()
        converter.update_rate("usd", 1.1, TODAY)
        converter.update_rate("BYN", 3.5, TODAY)
        self.assertEqual(converter.convert(110.0, "USD", "BYN"), 350.0)
        self.assertEqual(converter.last_updated, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            converter.update_rate("XXX", 0, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            converter.convert(1.0, "XXX", "EUR")

    def test_sales_report(self):
        self.booking.confirm()
        report = SalesReport(TODAY, START, [self.booking])
        self.assertEqual(report.calculate_revenue(), self.booking.total_price)
        self.assertEqual(report.average_check(), self.booking.total_price)
        self.assertEqual(report.top_destinations(), [("Анталья", 1)])
        self.assertEqual(SalesReport(START, START, [self.booking]).average_check(), 0.0)


if __name__ == "__main__":
    unittest.main()
