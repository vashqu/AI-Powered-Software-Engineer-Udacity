# Personal Finance Manager — Design Patterns Project

A modular Python personal finance manager built for Udacity's **AI Powered Software Engineer** course. It tracks income and expenses, monitors the user's net balance, adapts external freelance invoices into internal transactions, triggers low-balance alerts, and supports undoable transaction history using four classic object-oriented design patterns and Dependency Injection.

## Project Structure

```text
starter/
├── main.py                                  # Simulation entry point demonstrating all 4 patterns
├── balance/
│   ├── balance.py                           # Singleton Balance + Observer subject
│   ├── balance_observer.py                  # IBalanceObserver, PrintObserver, LowBalanceAlertObserver
│   ├── test_balance.py                      # Unit tests for Singleton Balance & observer management
│   └── test_balance_observer.py             # Unit tests for observers & DI output handlers
└── transaction/
    ├── transaction.py                       # Transaction model
    ├── transaction_category.py              # TransactionCategory Enum (INCOME, EXPENSE)
    ├── external_income_transaction.py       # Third-party freelance income model
    ├── transaction_adapter.py               # Adapter converting external income -> Transaction
    ├── transaction_command.py               # Command pattern (ApplyTransactionCommand, TransactionManager)
    ├── test_transaction.py                  # Unit tests for Transaction
    ├── test_transaction_adapter.py          # Unit tests for TransactionAdapter
    └── test_transaction_command.py          # Unit tests for Command pattern & DI isolation
```

## Run It

Requires Python 3.10+ (uses only the standard library and `unittest`).

```bash
cd cd14600-project-starter/starter

# Run the simulation
python3 main.py

# Run all unit tests (27 tests)
python3 -m unittest discover -v

# Run a single test module
python3 -m unittest balance/test_balance_observer.py
```

## Design Patterns & Dependency Injection

1. **Singleton (`Balance`)** — [balance.py](starter/balance/balance.py)
   - Enforces a single shared source of truth for the user's net balance via `Balance.get_instance()` and blocks accidental direct instantiation (`Balance()`).
   - Provides `reset()` to clear both the balance and registered observers cleanly between test runs.

2. **Adapter (`TransactionAdapter`)** — [transaction_adapter.py](starter/transaction/transaction_adapter.py)
   - Translates third-party `ExternalFreelanceIncome` objects (with `invoice_id`, `description`, and string `typ`) into standard internal `Transaction` objects using `TransactionCategory`.
   - Keeps `Balance` and `Transaction` completely unaware of external vendor formats.

3. **Observer (`IBalanceObserver`, `PrintObserver`, `LowBalanceAlertObserver`)** — [balance_observer.py](starter/balance/balance_observer.py)
   - Decouples balance state changes from side effects such as console logging and threshold alerts.
   - New reactions (e.g., email/SMS alerts or persistence loggers) can be added by implementing `IBalanceObserver` without modifying `Balance`.

4. **Command (`ITransactionCommand`, `ApplyTransactionCommand`, `TransactionManager`)** — [transaction_command.py](starter/transaction/transaction_command.py)
   - Chosen as the fourth pattern to encapsulate each financial operation as an object with `execute()` and `undo()`, managed by a `TransactionManager` invoker that supports undo, redo, and an audit history.
   - Improves **flexibility** (new commands such as transfers or scheduled payments fit the same interface), **testability** (commands accept their `balance` receiver via constructor Dependency Injection instead of calling `Balance.get_instance()` directly), and **scalability** (enables undo/redo stacks, queuing, and transaction replay).

5. **Dependency Injection**
   - `ApplyTransactionCommand(balance, transaction)` receives its `balance` receiver via constructor injection, allowing unit tests to substitute a lightweight fake balance instead of relying on global Singleton state.
   - `PrintObserver(output_handler=print)` and `LowBalanceAlertObserver(threshold, alert_handler=print)` inject their output/alert callbacks, making side effects easy to verify in unit tests without monkey-patching `builtins.print`.

## Reflection

### How the Design Patterns Improved the Application
- **Separation of concerns:** Each class has a single clear job — `Balance` owns state and observer notification, `TransactionAdapter` handles external schema translation, observers handle reactions, and `ApplyTransactionCommand` / `TransactionManager` handle execution lifecycle and history.
- **Open/Closed extensibility:** Adding a new external income provider only requires a new adapter; adding a new notification channel only requires a new `IBalanceObserver`; adding a new reversible financial action only requires a new `ITransactionCommand`.
- **Testability through Dependency Injection:** Injecting `balance` into commands and output callbacks into observers lets unit tests run deterministically in milliseconds with zero global side effects.

### Trade-offs Encountered
- **Singleton vs. Test Isolation:** While Singleton guarantees one balance across the app, shared global state can leak between unit tests if not carefully managed. Having `reset()` clear both `_balance` and `_observers` solved this, and injecting `balance` into commands avoided spreading calls to `Balance.get_instance()` throughout the codebase.
- **Undo Semantics & Observer Notifications:** Implementing `undo()` by applying an inverse transaction keeps observers (such as `LowBalanceAlertObserver`) accurately synchronized when a deposit is undone, though in a production ledger you would also distinguish reversal entries from regular expenses in reporting.
- **Added Indirection:** Wrapping simple transactions in command and adapter classes introduces more files and small classes than a procedural script, which is only worthwhile when the system needs extensibility, history/undo, or multiple external integrations.

## License

[License](LICENSE.txt)
