import unittest
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_command import (
    ApplyTransactionCommand,
    TransactionManager,
)


class _FakeBalance:
    """Lightweight fake receiver to test commands in isolation via Dependency Injection."""

    def __init__(self):
        self.applied = []

    def apply_transaction(self, transaction):
        self.applied.append(transaction)


class TestTransactionCommand(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_command_works_with_injected_fake_balance(self):
        fake_balance = _FakeBalance()
        txn = Transaction(250, TransactionCategory.INCOME, description="Consulting")
        cmd = ApplyTransactionCommand(fake_balance, txn)

        cmd.execute()
        self.assertEqual(fake_balance.applied, [txn])

        cmd.undo()
        self.assertEqual(len(fake_balance.applied), 2)
        self.assertEqual(
            fake_balance.applied[1],
            Transaction(250, TransactionCategory.EXPENSE),
        )
        self.assertEqual(fake_balance.applied[1].description, "Undo: Consulting")

    def test_double_execute_raises_runtime_error(self):
        cmd = ApplyTransactionCommand(
            self.balance, Transaction(100, TransactionCategory.INCOME)
        )
        cmd.execute()
        with self.assertRaises(RuntimeError):
            cmd.execute()

    def test_undo_before_execute_raises_runtime_error(self):
        cmd = ApplyTransactionCommand(
            self.balance, Transaction(100, TransactionCategory.INCOME)
        )
        with self.assertRaises(RuntimeError):
            cmd.undo()

    def test_manager_execute_undo_redo_and_history(self):
        manager = TransactionManager()
        cmd1 = ApplyTransactionCommand(
            self.balance, Transaction(200, TransactionCategory.INCOME)
        )
        cmd2 = ApplyTransactionCommand(
            self.balance, Transaction(75, TransactionCategory.EXPENSE)
        )

        manager.execute_command(cmd1)
        manager.execute_command(cmd2)
        self.assertEqual(self.balance.get_balance(), 125)
        self.assertEqual(len(manager.get_history()), 2)

        undone = manager.undo_last()
        self.assertIs(undone, cmd2)
        self.assertEqual(self.balance.get_balance(), 200)
        self.assertEqual(len(manager.get_history()), 1)

        redone = manager.redo_last()
        self.assertIs(redone, cmd2)
        self.assertEqual(self.balance.get_balance(), 125)
        self.assertEqual(len(manager.get_history()), 2)

    def test_manager_undo_and_redo_when_empty_return_none(self):
        manager = TransactionManager()
        self.assertIsNone(manager.undo_last())
        self.assertIsNone(manager.redo_last())

    def test_undo_notifies_observers(self):
        alerts = []
        observer = LowBalanceAlertObserver(threshold=100, alert_handler=alerts.append)
        self.balance.register_observer(observer)

        manager = TransactionManager()
        manager.execute_command(
            ApplyTransactionCommand(
                self.balance, Transaction(150, TransactionCategory.INCOME)
            )
        )
        self.assertFalse(observer.alert_triggered)

        manager.undo_last()
        self.assertEqual(self.balance.get_balance(), 0.0)
        self.assertTrue(observer.alert_triggered)
        self.assertEqual(len(alerts), 1)


if __name__ == "__main__":
    unittest.main()
