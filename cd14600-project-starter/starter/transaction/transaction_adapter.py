# transaction_adapter.py

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TransactionAdapter:
    """Adapts external third-party transactions into Transaction instances."""

    _TYPE_MAP = {
        "income": TransactionCategory.INCOME,
        "expense": TransactionCategory.EXPENSE,
    }

    def __init__(self, external_transaction):
        self.external_transaction = external_transaction

    def to_transaction(self) -> Transaction:
        """Convert an external transaction to a standard Transaction."""
        ext = self.external_transaction
        raw_type = getattr(ext, "typ", None)
        if (
            not isinstance(raw_type, str)
            or raw_type.lower() not in self._TYPE_MAP
        ):
            raise ValueError(
                f"Unsupported external transaction type: {raw_type!r}"
            )

        category = self._TYPE_MAP[raw_type.lower()]
        invoice_id = getattr(ext, "invoice_id", "")
        details = getattr(ext, "description", "")
        description = (
            f"[{invoice_id}] {details}".strip() if invoice_id else details
        )

        return Transaction(ext.amount, category, description=description)
