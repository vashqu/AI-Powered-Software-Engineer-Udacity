# Udatracker

Udatracker is a small order-tracking application, built test-first (Red → Green → Refactor) as part of Udacity's AI Powered Software Engineer course. A Flask REST API sits on top of an `OrderTracker` class that holds the business logic, and a simple frontend lets you add, update and filter orders in the browser.

## What was built

```
.
├── backend
│   ├── app.py                  # Flask routes (the REST API) + serves the frontend
│   ├── order_tracker.py        # OrderTracker: validation and business rules
│   ├── in_memory_storage.py    # Storage backend (a dict; data is lost on restart)
│   ├── requirements.txt
│   └── tests
│       ├── test_order_tracker.py   # Unit tests (storage is mocked)
│       └── test_api.py             # API tests (Flask test client)
├── frontend                    # index.html, css/, js/
├── Dockerfile                  # Lightweight image for the app
├── .dockerignore
└── pytest.ini
```

### Orders
An order is a JSON object with exactly five keys:

```json
{"order_id": "ORD1", "item_name": "Laptop", "quantity": 2, "customer_id": "CUST1", "status": "pending"}
```

`status` is one of `pending`, `processing`, `shipped`, `delivered`, `cancelled` (default `pending`). There is no delete operation.

### OrderTracker
| Method | Behaviour |
|---|---|
| `add_order` | Validates all fields, rejects duplicate ids, saves and returns the order |
| `get_order_by_id` | Returns the order, or `None` if it does not exist |
| `update_order_status` | Requires the order to exist and the new status to be valid; saves an updated *copy* |
| `list_all_orders` | Returns all orders as a list of dicts |
| `list_orders_by_status` | Returns only orders with the given (valid) status |

Validation errors are `ValueError`s with fixed, explicit messages, e.g. `Order with ID 'ORD1' already exists.`

### REST API
| Endpoint | Success | Errors |
|---|---|---|
| `POST /api/orders` | 201 + order | 400 invalid input, 409 duplicate id |
| `GET /api/orders/<id>` | 200 + order | 404 not found |
| `PUT /api/orders/<id>/status` (body `{"new_status": ...}`) | 200 + updated order | 400 invalid status/body, 404 not found |
| `GET /api/orders` | 200 + list | – |
| `GET /api/orders?status=<status>` | 200 + filtered list | 400 invalid status |

Errors are always returned as `{"error": "<message>"}`.

## Running it

From this `starter/` directory:

```bash
source venv/bin/activate
pip install -r backend/requirements.txt
python -m backend.app          # http://127.0.0.1:8000/
pytest                         # run all tests
```

Set `FLASK_DEBUG=1` to enable Flask's debug mode and auto-reloader locally. It is off by default.

### Running with Docker

The `Dockerfile` builds a small image (`python:3.12-slim`, non-root user) containing the backend and the frontend. Tests and the virtualenv are excluded.

```bash
docker build -t udatracker .                 # build the image (from starter/)
docker run --rm -p 8000:8000 udatracker      # start it, then open http://localhost:8000/
```

Stop it with Ctrl-C. Data is held in memory, so orders are lost whenever the container stops. To run the tests inside the image, mount them in:

```bash
docker run --rm -v "$PWD/backend/tests:/app/backend/tests" -v "$PWD/pytest.ini:/app/pytest.ini" \
  udatracker sh -c "pip install -q pytest==8.4.1 && pytest"
```

## Reflection

**Trade-off:** the tracker raises `ValueError` for every problem, but the API must distinguish 404 and 409 from 400. Rather than parse messages, I added `ValueError` subclasses for duplicate and missing orders; existing handlers keep working and the routes choose status codes by type.

**Testing insight:** mocking storage let tests verify behaviour, not just results, such as `save_order` never being called after a failed validation. Three tests passed against empty stubs, a reminder to treat any green test during the Red phase with suspicion.

**Next step:** replace `InMemoryStorage` with SQLite so orders persist; the tracker only needs three storage methods, so it should not change.
