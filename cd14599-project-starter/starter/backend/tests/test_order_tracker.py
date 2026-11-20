import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- Tests ---
#
# Conventions used below:
#   * ValueError is raised for every validation / not-found problem.
#   * Error messages are asserted EXACTLY (via re.escape + match) so they stay stable.
#   * Each test checks one behaviour. Storage is a Mock, so we also verify
#     how OrderTracker talks to storage (save_order / get_order / get_all_orders).

import re

VALID_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]
STATUS_ERROR = "Invalid status '{status}'. Must be one of: pending, processing, shipped, delivered, cancelled."


def make_order(order_id="ORD1", item_name="Laptop", quantity=2, customer_id="CUST1", status="pending"):
    """Helper: a stored order record with exactly the five keys."""
    return {
        "order_id": order_id,
        "item_name": item_name,
        "quantity": quantity,
        "customer_id": customer_id,
        "status": status,
    }


def error_message(text):
    """Helper: exact-match regex for pytest.raises(match=...)."""
    return f"^{re.escape(text)}$"


# ---------------------------------------------------------------------------
# __init__ (storage contract)
# ---------------------------------------------------------------------------

def test_init_rejects_storage_missing_required_method():
    class BadStorage:
        def save_order(self, order_id, order_data): ...
        def get_order(self, order_id): ...
        # get_all_orders is missing

    with pytest.raises(TypeError, match=error_message("Storage object must implement a callable 'get_all_orders' method.")):
        OrderTracker(BadStorage())


# ---------------------------------------------------------------------------
# add_order
# ---------------------------------------------------------------------------

def test_add_order_returns_order_with_the_five_keys(order_tracker):
    result = order_tracker.add_order("ORD1", "Laptop", 2, "CUST1")
    assert result == make_order()


def test_add_order_defaults_status_to_pending(order_tracker):
    result = order_tracker.add_order("ORD1", "Laptop", 2, "CUST1")
    assert result["status"] == "pending"


@pytest.mark.parametrize("status", VALID_STATUSES)
def test_add_order_accepts_every_valid_status(order_tracker, status):
    result = order_tracker.add_order("ORD1", "Laptop", 2, "CUST1", status=status)
    assert result["status"] == status


def test_add_order_saves_order_to_storage(order_tracker, mock_storage):
    order_tracker.add_order("ORD1", "Laptop", 2, "CUST1")
    mock_storage.save_order.assert_called_once_with("ORD1", make_order())


def test_add_order_checks_storage_for_existing_id(order_tracker, mock_storage):
    order_tracker.add_order("ORD1", "Laptop", 2, "CUST1")
    mock_storage.get_order.assert_called_once_with("ORD1")


def test_add_order_rejects_duplicate_id(order_tracker, mock_storage):
    mock_storage.get_order.return_value = make_order()
    with pytest.raises(ValueError, match=error_message("Order with ID 'ORD1' already exists.")):
        order_tracker.add_order("ORD1", "Laptop", 2, "CUST1")


def test_add_order_does_not_save_duplicate(order_tracker, mock_storage):
    mock_storage.get_order.return_value = make_order()
    with pytest.raises(ValueError):
        order_tracker.add_order("ORD1", "Laptop", 2, "CUST1")
    mock_storage.save_order.assert_not_called()


@pytest.mark.parametrize("bad_id", ["", "   ", None, 123])
def test_add_order_rejects_invalid_order_id(order_tracker, bad_id):
    with pytest.raises(ValueError, match=error_message("Order ID must be a non-empty string.")):
        order_tracker.add_order(bad_id, "Laptop", 2, "CUST1")


@pytest.mark.parametrize("bad_name", ["", "   ", None, 123])
def test_add_order_rejects_invalid_item_name(order_tracker, bad_name):
    with pytest.raises(ValueError, match=error_message("Item name must be a non-empty string.")):
        order_tracker.add_order("ORD1", bad_name, 2, "CUST1")


@pytest.mark.parametrize("bad_quantity", [0, -1, 1.5, "2", None, True])
def test_add_order_rejects_invalid_quantity(order_tracker, bad_quantity):
    with pytest.raises(ValueError, match=error_message("Quantity must be a positive integer.")):
        order_tracker.add_order("ORD1", "Laptop", bad_quantity, "CUST1")


@pytest.mark.parametrize("bad_customer", ["", "   ", None, 123])
def test_add_order_rejects_invalid_customer_id(order_tracker, bad_customer):
    with pytest.raises(ValueError, match=error_message("Customer ID must be a non-empty string.")):
        order_tracker.add_order("ORD1", "Laptop", 2, bad_customer)


@pytest.mark.parametrize("bad_status", ["unknown", "PENDING", "", None])
def test_add_order_rejects_invalid_status(order_tracker, bad_status):
    with pytest.raises(ValueError, match=error_message(STATUS_ERROR.format(status=bad_status))):
        order_tracker.add_order("ORD1", "Laptop", 2, "CUST1", status=bad_status)


def test_add_order_does_not_save_when_validation_fails(order_tracker, mock_storage):
    with pytest.raises(ValueError):
        order_tracker.add_order("ORD1", "Laptop", 0, "CUST1")
    mock_storage.save_order.assert_not_called()


# ---------------------------------------------------------------------------
# get_order_by_id
# ---------------------------------------------------------------------------

def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    mock_storage.get_order.return_value = make_order()
    assert order_tracker.get_order_by_id("ORD1") == make_order()


def test_get_order_by_id_asks_storage_for_that_id(order_tracker, mock_storage):
    order_tracker.get_order_by_id("ORD1")
    mock_storage.get_order.assert_called_once_with("ORD1")


def test_get_order_by_id_returns_none_when_missing(order_tracker):
    assert order_tracker.get_order_by_id("NOPE") is None


# ---------------------------------------------------------------------------
# update_order_status
# ---------------------------------------------------------------------------

def test_update_order_status_returns_order_with_new_status(order_tracker, mock_storage):
    mock_storage.get_order.return_value = make_order(status="pending")
    result = order_tracker.update_order_status("ORD1", "shipped")
    assert result == make_order(status="shipped")


def test_update_order_status_saves_updated_order(order_tracker, mock_storage):
    mock_storage.get_order.return_value = make_order(status="pending")
    order_tracker.update_order_status("ORD1", "shipped")
    mock_storage.save_order.assert_called_once_with("ORD1", make_order(status="shipped"))


def test_update_order_status_does_not_mutate_dict_from_storage(order_tracker, mock_storage):
    stored = make_order(status="pending")
    mock_storage.get_order.return_value = stored
    order_tracker.update_order_status("ORD1", "shipped")
    assert stored["status"] == "pending"  # copy -> update -> save, never in-place


def test_update_order_status_only_changes_status(order_tracker, mock_storage):
    mock_storage.get_order.return_value = make_order(status="pending")
    result = order_tracker.update_order_status("ORD1", "processing")
    assert {k: v for k, v in result.items() if k != "status"} == \
           {k: v for k, v in make_order().items() if k != "status"}


@pytest.mark.parametrize("new_status", VALID_STATUSES)
def test_update_order_status_accepts_every_valid_status(order_tracker, mock_storage, new_status):
    mock_storage.get_order.return_value = make_order(status="pending")
    assert order_tracker.update_order_status("ORD1", new_status)["status"] == new_status


def test_update_order_status_raises_when_order_missing(order_tracker):
    with pytest.raises(ValueError, match=error_message("Order with ID 'NOPE' not found.")):
        order_tracker.update_order_status("NOPE", "shipped")


def test_update_order_status_rejects_invalid_status(order_tracker, mock_storage):
    mock_storage.get_order.return_value = make_order()
    with pytest.raises(ValueError, match=error_message(STATUS_ERROR.format(status="lost"))):
        order_tracker.update_order_status("ORD1", "lost")


def test_update_order_status_does_not_save_on_invalid_status(order_tracker, mock_storage):
    mock_storage.get_order.return_value = make_order()
    with pytest.raises(ValueError):
        order_tracker.update_order_status("ORD1", "lost")
    mock_storage.save_order.assert_not_called()


def test_update_order_status_does_not_save_when_order_missing(order_tracker, mock_storage):
    with pytest.raises(ValueError):
        order_tracker.update_order_status("NOPE", "shipped")
    mock_storage.save_order.assert_not_called()


# ---------------------------------------------------------------------------
# list_all_orders
# ---------------------------------------------------------------------------

def test_list_all_orders_returns_empty_list_when_no_orders(order_tracker):
    assert order_tracker.list_all_orders() == []


def test_list_all_orders_returns_a_list(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {"ORD1": make_order("ORD1")}
    assert isinstance(order_tracker.list_all_orders(), list)


def test_list_all_orders_returns_every_order_as_dict(order_tracker, mock_storage):
    a, b = make_order("A"), make_order("B", status="shipped")
    mock_storage.get_all_orders.return_value = {"A": a, "B": b}
    assert order_tracker.list_all_orders() == [a, b]


# ---------------------------------------------------------------------------
# list_orders_by_status
# ---------------------------------------------------------------------------

def test_list_orders_by_status_returns_only_matching_orders(order_tracker, mock_storage):
    pending = make_order("A", status="pending")
    shipped = make_order("B", status="shipped")
    mock_storage.get_all_orders.return_value = {"A": pending, "B": shipped}
    assert order_tracker.list_orders_by_status("pending") == [pending]


def test_list_orders_by_status_returns_empty_list_when_none_match(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {"A": make_order("A", status="pending")}
    assert order_tracker.list_orders_by_status("delivered") == []


def test_list_orders_by_status_returns_multiple_matches(order_tracker, mock_storage):
    a = make_order("A", status="shipped")
    b = make_order("B", status="shipped")
    c = make_order("C", status="pending")
    mock_storage.get_all_orders.return_value = {"A": a, "B": b, "C": c}
    assert order_tracker.list_orders_by_status("shipped") == [a, b]


@pytest.mark.parametrize("status", VALID_STATUSES)
def test_list_orders_by_status_accepts_every_valid_status(order_tracker, status):
    assert order_tracker.list_orders_by_status(status) == []


@pytest.mark.parametrize("bad_status", ["unknown", "SHIPPED", "", None])
def test_list_orders_by_status_rejects_invalid_status(order_tracker, bad_status):
    with pytest.raises(ValueError, match=error_message(STATUS_ERROR.format(status=bad_status))):
        order_tracker.list_orders_by_status(bad_status)
