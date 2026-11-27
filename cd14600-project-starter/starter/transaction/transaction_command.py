# transaction_command.py

from abc import ABC, abstractmethod
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class ITransactionCommand(ABC):
    """Command interface for executable and undoable financial actions."""

    @abstractmethod
    def execute(self):
        """Execute the command."""

    @abstractmethod
    def undo(self):
        """Reverse the effects of the command."""


class ApplyTransactionCommand(ITransactionCommand):
    """
    Encapsulates applying a Transaction to a Balance receiver.

    Uses Dependency Injection by accepting the balance receiver in __init__
    rather than calling Balance.get_instance() directly, making the command
    decoupled from global state and straightforward to unit test with mocks.
    """

    def __init__(self, balance, transaction: Transaction):
        self._balance = balance
        self.transaction = transaction
        self._executed = False

    def execute(self):
        """Apply the wrapped transaction to the injected balance."""
        if self._executed:
            raise RuntimeError("Command has already been executed.")
        self._balance.apply_transaction(self.transaction)
        self._executed = True

    def undo(self):
        """Apply an inverse transaction to reverse the original change."""
        if not self._executed:
            raise RuntimeError(
                "Cannot undo a command that has not been executed."
            )

        if self.transaction.category == TransactionCategory.INCOME:
            reverse_category = TransactionCategory.EXPENSE
        elif self.transaction.category == TransactionCategory.EXPENSE:
            reverse_category = TransactionCategory.INCOME
        else:
            raise ValueError(
                "Cannot undo transaction with invalid category: "
                f"{self.transaction.category}"
            )

        reverse_desc = (
            f"Undo: {self.transaction.description}"
            if self.transaction.description
            else "Undo"
        )
        reverse_txn = Transaction(
            self.transaction.amount, reverse_category, description=reverse_desc
        )
        self._balance.apply_transaction(reverse_txn)
        self._executed = False


class TransactionManager:
    """Invoker that executes commands and maintains undo/redo history."""

    def __init__(self):
        self._history = []
        self._redo_stack = []

    def execute_command(self, command: ITransactionCommand):
        """Execute a command, record it in history, and clear redo stack."""
        command.execute()
        self._history.append(command)
        self._redo_stack.clear()

    def undo_last(self):
        """Undo the most recently executed command, or return None."""
        if not self._history:
            return None
        command = self._history.pop()
        command.undo()
        self._redo_stack.append(command)
        return command

    def redo_last(self):
        """Re-execute the most recently undone command, or return None."""
        if not self._redo_stack:
            return None
        command = self._redo_stack.pop()
        command.execute()
        self._history.append(command)
        return command

    def get_history(self):
        """Return a shallow copy of executed commands in order."""
        return list(self._history)
