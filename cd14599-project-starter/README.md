# Udatracker

Udatracker is an order-management web app built test-first (Test-Driven Development) for Udacity's AI Powered Software Engineer course. It has a Python/Flask REST API, an `OrderTracker` class holding the business logic, and a single-page frontend.

<img width="1261" height="805" alt="Screenshot of the Udatracker web application" src="https://github.com/user-attachments/assets/375894d2-6b0b-43a6-aca9-e0e8cc52d20a"/>

## What it looks like

A single page titled **Order Management System**, made of four sections:

- **Add New Order:** a form with Order ID, Item Name, Quantity and Customer ID. New orders start as `pending`.
- **Get Order Details:** enter an Order ID and see that order's JSON.
- **Update Order Status:** enter an Order ID, pick `pending`, `processing`, `shipped`, `delivered` or `cancelled`, and click Update.
- **All Orders:** a table (ID, Item, Qty, Customer, Status) with a Refresh button and a status filter. Success and error messages (for example a duplicate id or an unknown order) appear on the page.

## What was built

- **`OrderTracker`** ([order_tracker.py](starter/backend/order_tracker.py)): add an order (validated, no duplicate ids), get one by id, update its status, list all orders, and list orders by status. There is no delete.
- **REST API** ([app.py](starter/backend/app.py)): `POST /api/orders`, `GET /api/orders/<id>`, `PUT /api/orders/<id>/status`, and `GET /api/orders` with an optional `?status=` filter. Successes return JSON with 200 or 201; failures return `{"error": "..."}` with 400, 404 or 409.
- **Tests** (88): unit tests for `OrderTracker` with mocked storage, and integration tests for every endpoint including error paths.
- **Docker:** a lightweight `Dockerfile` for running the app in a container.

## Run it

```bash
cd starter
source venv/bin/activate
pip install -r backend/requirements.txt
python -m backend.app        # open http://127.0.0.1:8000/
pytest                       # run the tests
```

For the full structure, API reference, Docker instructions and a short reflection on the project, see [starter/README.md](starter/README.md).
