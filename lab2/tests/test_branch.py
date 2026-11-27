import unittest
from tests.factories import TODAY, make_city, make_person
from travel_agency.company.company import Branch
from travel_agency.exceptions import EmployeeNotFoundException, InvalidClientDataException
from travel_agency.geography.places import Address
from travel_agency.people.staff import Employee


class BranchTest(unittest.TestCase):
    def test_staff(self):
        branch = Branch("Офис", Address("Ленина", "1", "1", make_city()), 9, 18)
        employee = Employee("E1", make_person(), "Кассир", 1000.0, TODAY)
        branch.hire_employee(employee)
        self.assertIs(employee.branch, branch)
        with self.assertRaises(InvalidClientDataException):
            branch.hire_employee(employee)
        self.assertEqual(branch.calculate_payroll(), 1000.0)
        self.assertTrue(branch.is_open_at(10))
        self.assertIs(branch.fire_employee("E1"), employee)
        self.assertIsNone(employee.branch)
        with self.assertRaises(EmployeeNotFoundException):
            branch.fire_employee("E1")


if __name__ == "__main__":
    unittest.main()
