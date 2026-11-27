# transaction.py

from transaction.transaction_category import TransactionCategory


class Transaction:
    """Represents a financial transaction with an amount and category."""

    def __init__(
        self,
        amount,
        category: TransactionCategory,
        description: str = "",
    ):
        self.amount = amount
        self.category = category
        self.description = description

    def __str__(self):
        return f"Transaction(${self.amount}, category='{self.category}')"

    def __repr__(self):
        return (
            f"Transaction(amount={self.amount!r}, category={self.category!r}, "
            f"description={self.description!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return self.amount == other.amount and self.category == other.category
