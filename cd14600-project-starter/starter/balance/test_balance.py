import unittest
from balance.balance import Balance
from balance.balance_observer import IBalanceObserver
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class _RecordingObserver(IBalanceObserver):
    def __init__(self):
        self.events = []

    def update(self, balance, transaction):
        self.events.append((balance, transaction))


class TestBalance(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_initial_balance(self):
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_singleton_instance(self):
        balance1 = Balance.get_instance()
        balance2 = Balance.get_instance()
        self.assertIs(balance1, balance2)

    def test_direct_instantiation_raises_error(self):
        with self.assertRaises(RuntimeError):
            Balance()

    def test_add_income(self):
        self.balance.add_income(100)
        self.assertEqual(self.balance.get_balance(), 100)

    def test_add_expense(self):
        self.balance.add_expense(40)
        self.assertEqual(self.balance.get_balance(), -40)

    def test_negative_amounts_raise_value_error(self):
        with self.assertRaises(ValueError):
            self.balance.add_income(-10)
        with self.assertRaises(ValueError):
            self.balance.add_expense(-5)

    def test_apply_transaction_income(self):
        t = Transaction(150, TransactionCategory.INCOME)
        self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), 150)

    def test_apply_transaction_expense(self):
        t = Transaction(60, TransactionCategory.EXPENSE)
        self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), -60)

    def test_apply_transaction_invalid_category(self):
        class FakeCategory:
            pass
        t = Transaction(100, FakeCategory())
        with self.assertRaises(ValueError):
            self.balance.apply_transaction(t)

    def test_reset(self):
        self.balance.add_income(100)
        self.balance.add_expense(50)
        self.balance.reset()
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_summary(self):
        self.balance.add_income(125.5)
        self.assertEqual(
            self.balance.summary(), "Current Net Balance: $125.50"
        )

    def test_unregister_observer_stops_notifications(self):
        observer = _RecordingObserver()
        self.balance.register_observer(observer)
        self.balance.apply_transaction(
            Transaction(50, TransactionCategory.INCOME)
        )
        self.assertEqual(len(observer.events), 1)

        self.balance.unregister_observer(observer)
        self.balance.apply_transaction(
            Transaction(25, TransactionCategory.INCOME)
        )
        self.assertEqual(len(observer.events), 1)


if __name__ == "__main__":
    unittest.main()
