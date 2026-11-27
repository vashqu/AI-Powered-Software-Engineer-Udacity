# balance_observer.py

from typing import Callable


class IBalanceObserver:
    """Observer interface for components that react to balance updates."""

    def update(self, balance, transaction):
        """Handle balance updates."""
        raise NotImplementedError("Subclasses must implement update method.")


class PrintObserver(IBalanceObserver):
    """Logs every balance update using an injectable output handler."""

    def __init__(self, output_handler: Callable[[str], None] = print):
        self._output_handler = output_handler

    def update(self, balance, transaction):
        """Print balance update message."""
        desc = getattr(transaction, "description", "")
        details = f" ({desc})" if desc else ""
        self._output_handler(
            f"[Balance Update] {transaction}{details} "
            f"-> Current Balance: ${balance:.2f}"
        )


class LowBalanceAlertObserver(IBalanceObserver):
    """Triggers an alert when the balance drops below a defined threshold."""

    def __init__(
        self,
        threshold: float,
        alert_handler: Callable[[str], None] = print,
    ):
        self.threshold = threshold
        self._alert_handler = alert_handler
        self.alert_triggered = False

    def update(self, balance, transaction):
        """Alert if balance drops below threshold."""
        if balance < self.threshold:
            self.alert_triggered = True
            self._alert_handler(
                f"[LOW BALANCE ALERT] Balance (${balance:.2f}) "
                f"is below threshold (${self.threshold:.2f})!"
            )
        else:
            self.alert_triggered = False
