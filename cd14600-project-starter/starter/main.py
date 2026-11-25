"""This module serves as the entry point for the program."""

from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver, PrintObserver
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction import Transaction
from transaction.transaction_adapter import TransactionAdapter
from transaction.transaction_category import TransactionCategory
from transaction.transaction_command import (
    ApplyTransactionCommand,
    TransactionManager,
)


def main():
    print("=== Personal Finance Manager Simulation ===\n")

    # 1. Singleton Pattern: retrieve the single shared Balance instance
    balance = Balance.get_instance()
    balance.reset()

    # 2. Observer Pattern: register observers for live logging and low-balance alerts
    balance.register_observer(PrintObserver())
    balance.register_observer(LowBalanceAlertObserver(threshold=100))

    # 3. Standard transactions
    transactions = [
        Transaction(100, TransactionCategory.INCOME, description="Initial deposit"),
        Transaction(50, TransactionCategory.EXPENSE, description="Groceries"),
        Transaction(200, TransactionCategory.INCOME, description="Side gig"),
        Transaction(75, TransactionCategory.EXPENSE, description="Utilities"),
    ]

    # 4. Adapter Pattern: convert external freelance income into a standard Transaction
    freelance_income = ExternalFreelanceIncome(
        1200, "INV-98765", "Mobile App Project"
    )
    adapter = TransactionAdapter(freelance_income)
    adapted_transaction = adapter.to_transaction()

    all_transactions = transactions + [adapted_transaction]

    # 5. Command Pattern + Dependency Injection: execute transactions via commands
    manager = TransactionManager()
    print("Applying transactions...")
    for txn in all_transactions:
        command = ApplyTransactionCommand(balance, txn)
        manager.execute_command(command)

    print(f"\n{balance.summary()}")
    print(f"Transactions in history: {len(manager.get_history())}")

    # Demonstrate Command Pattern undo & redo
    print("\nUndoing last transaction (freelance invoice)...")
    manager.undo_last()
    print(balance.summary())

    print("\nRedoing last transaction...")
    manager.redo_last()
    print(balance.summary())


if __name__ == "__main__":
    main()
