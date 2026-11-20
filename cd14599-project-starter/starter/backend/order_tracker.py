# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

VALID_STATUSES = ("pending", "processing", "shipped", "delivered", "cancelled")


class OrderNotFoundError(ValueError):
    """Raised when an order id does not exist. Subclasses ValueError so callers
    that only care about "bad input" can catch ValueError, while the API can
    map this one to HTTP 404."""


class DuplicateOrderError(ValueError):
    """Raised when adding an order whose id already exists (API -> HTTP 409)."""


def _is_non_empty_string(value):
    return isinstance(value, str) and value.strip() != ""


def _validate_status(status):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}.")


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        if not _is_non_empty_string(order_id):
            raise ValueError("Order ID must be a non-empty string.")
        if not _is_non_empty_string(item_name):
            raise ValueError("Item name must be a non-empty string.")
        # bool is a subclass of int, so exclude it explicitly
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        if not _is_non_empty_string(customer_id):
            raise ValueError("Customer ID must be a non-empty string.")
        _validate_status(status)

        if self.storage.get_order(order_id) is not None:
            raise DuplicateOrderError(f"Order with ID '{order_id}' already exists.")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order)
        return order

    def get_order_by_id(self, order_id: str):
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        existing = self.storage.get_order(order_id)
        if existing is None:
            raise OrderNotFoundError(f"Order with ID '{order_id}' not found.")
        _validate_status(new_status)

        updated = {**existing, "status": new_status}  # copy, never mutate storage's dict
        self.storage.save_order(order_id, updated)
        return updated

    def list_all_orders(self):
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        _validate_status(status)
        return [o for o in self.list_all_orders() if o.get("status") == status]
