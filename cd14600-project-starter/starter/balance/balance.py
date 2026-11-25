# balance.py

from transaction.transaction_category import TransactionCategory


class Balance:
    """Singleton to track the net balance and notify registered observers."""

    _instance = None
    _allow_instantiation = False

    def __init__(self):
        """Initialize the balance. Prevent direct instantiation."""
        if not Balance._allow_instantiation:
            raise RuntimeError(
                "Balance is a Singleton. Use Balance.get_instance() instead."
            )
        self._balance = 0.0
        self._observers = []

    @classmethod
    def get_instance(cls) -> "Balance":
        """Return the single Balance instance, creating it on first access."""
        if cls._instance is None:
            cls._allow_instantiation = True
            try:
                cls._instance = cls()
            finally:
                cls._allow_instantiation = False
        return cls._instance

    def reset(self):
        """Reset the net balance to zero and clear registered observers."""
        self._balance = 0.0
        self._observers.clear()

    def register_observer(self, observer):
        """Register an observer to be notified on balance changes."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer):
        """Remove a previously registered observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, transaction):
        """Notify all registered observers of a balance change."""
        for observer in list(self._observers):
            observer.update(self._balance, transaction)

    def add_income(self, amount):
        """Add income to the balance."""
        if amount < 0:
            raise ValueError("Income amount must be non-negative.")
        self._balance += amount

    def add_expense(self, amount):
        """Subtract expense from the balance."""
        if amount < 0:
            raise ValueError("Expense amount must be non-negative.")
        self._balance -= amount

    def apply_transaction(self, transaction):
        """
        Apply a Transaction object to update the balance and notify observers.

        Args:
            transaction (Transaction): The transaction to apply.
        """
        if transaction.category == TransactionCategory.INCOME:
            self.add_income(transaction.amount)
        elif transaction.category == TransactionCategory.EXPENSE:
            self.add_expense(transaction.amount)
        else:
            raise ValueError(f"Invalid transaction category: {transaction.category}")
        self.notify_observers(transaction)

    def get_balance(self):
        """Get the current net balance."""
        return self._balance

    def summary(self):
        """Return a summary string of the net balance."""
        return f"Current Net Balance: ${self._balance:.2f}"
