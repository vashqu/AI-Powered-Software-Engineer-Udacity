import unittest
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction_adapter import TransactionAdapter
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestTransactionAdapter(unittest.TestCase):

    def test_adapter_converts_freelance_income(self):
        ext_txn = ExternalFreelanceIncome(500, "INV-12345", "Website development")
        adapter = TransactionAdapter(ext_txn)
        txn = adapter.to_transaction()
        self.assertEqual(txn, Transaction(500, TransactionCategory.INCOME))
        self.assertEqual(txn.description, "[INV-12345] Website development")

    def test_adapter_rejects_unknown_external_type(self):
        class UnknownExternalTransaction:
            amount = 100
            typ = "crypto_swap"

        adapter = TransactionAdapter(UnknownExternalTransaction())
        with self.assertRaises(ValueError):
            adapter.to_transaction()


if __name__ == "__main__":
    unittest.main()
