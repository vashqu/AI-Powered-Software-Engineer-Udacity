import unittest
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from balance.balance import Balance
from balance.balance_observer import (
    IBalanceObserver,
    LowBalanceAlertObserver,
    PrintObserver,
)


class TestLowBalanceAlertObserver(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_alert_triggers_on_low_balance(self):
        alerts = []
        observer = LowBalanceAlertObserver(threshold=50, alert_handler=alerts.append)
        self.balance.register_observer(observer)

        self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertTrue(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertTrue(observer.alert_triggered)
        self.assertEqual(len(alerts), 2)

    def test_print_observer_uses_injected_output_handler(self):
        messages = []
        observer = PrintObserver(output_handler=messages.append)
        self.balance.register_observer(observer)

        txn = Transaction(75, TransactionCategory.INCOME, description="Bonus")
        self.balance.apply_transaction(txn)

        self.assertEqual(len(messages), 1)
        self.assertIn("$75", messages[0])
        self.assertIn("Bonus", messages[0])
        self.assertIn("$75.00", messages[0])

    def test_base_observer_raises_not_implemented(self):
        observer = IBalanceObserver()
        with self.assertRaises(NotImplementedError):
            observer.update(0.0, Transaction(10, TransactionCategory.INCOME))


if __name__ == "__main__":
    unittest.main()
