"""Тесты консольного интерфейса со сценарным вводом."""
import runpy
import unittest
from datetime import date, timedelta
from unittest.mock import patch

from travel_agency.cli.demo_data import FLIGHT_DAYS_AHEAD, build_demo_company
from travel_agency.cli.menu import TravelAgencyCli, main


def run_cli(commands):
    answers = iter(commands)
    output = []
    cli = TravelAgencyCli(build_demo_company(), lambda prompt: next(answers), output.append)
    cli.run()
    return "\n".join(output), cli


class CliTest(unittest.TestCase):
    def setUp(self):
        self.start = (date.today() + timedelta(days=FLIGHT_DAYS_AHEAD)).isoformat()
        self.today = date.today().isoformat()

    def test_show_and_search(self):
        output, _ = run_cli(["1", "2", "500", "6", "2", "1", "1", "x", "0"])
        self.assertIn("Вечный Рим", output)
        self.assertIn("Пляжи Антальи", output)
        self.assertIn("Подходящих туров нет", output)
        self.assertIn("Нет такого пункта меню", output)
        self.assertIn("До свидания!", output)

    def test_booking_flow(self):
        commands = ["4", "C2", "t2", self.start, "1", "5", "B0001", "123", "7", "C2", "8", self.today, self.today,
                    "9", "C2", "6", "B0001", "передумал", "0"]
        output, _ = run_cli(commands)
        self.assertIn("Создана бронь B0001", output)
        self.assertIn("Платёж P00001 проведён", output)
        self.assertIn("Анталья: продаж 1", output)
        self.assertIn("подтверждена", output)
        self.assertIn("Бронь отменена", output)

    def test_errors(self):
        commands = ["5", "B0001", "4", "C2", "T1", self.start, "1", "4", "C2", "T2", "не-дата",
                    "4", "C1", "T3", self.start, "1", "5", "B0001", "000", "7", "C2", "0"]
        output, _ = run_cli(commands)
        self.assertIn("Ошибка: Бронирование B0001 не найдено", output)
        self.assertIn("нужна виза", output)
        self.assertIn("Invalid isoformat", output)
        self.assertIn("CVV неверен", output)
        self.assertIn("У клиента нет бронирований", output)

    def test_register_client(self):
        commands = ["3", "C3", "Олег", "Котов", "1990-01-01", "+375", "oleg@mail.by", "MP3", "2035-01-01",
                    "4000000000000002", "321", "500", "0"]
        output, cli = run_cli(commands)
        self.assertIn("Клиент Олег Котов зарегистрирован", output)
        self.assertEqual(cli.company.find_client("C3").bank_card.balance, 500.0)

    def test_main(self):
        with patch("builtins.input", return_value="0"), patch("builtins.print") as fake_print:
            main()
        fake_print.assert_any_call("До свидания!")

    def test_module_entry_point(self):
        with patch("builtins.input", return_value="0"), patch("builtins.print") as fake_print:
            runpy.run_module("travel_agency", run_name="__main__")
        fake_print.assert_any_call("До свидания!")

    def test_main_interrupted(self):
        with patch("builtins.input", side_effect=EOFError), patch("builtins.print") as fake_print:
            main()
        fake_print.assert_any_call("\nРабота завершена")


if __name__ == "__main__":
    unittest.main()
