import os
from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker, OrderNotFoundError, DuplicateOrderError
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

def error_response(message, status_code):
    """All API errors share one JSON shape: {"error": "<message>"}."""
    return jsonify({"error": message}), status_code


@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("Request body must be a JSON object.", 400)
    try:
        order = order_tracker.add_order(
            order_id=data.get("order_id"),
            item_name=data.get("item_name"),
            quantity=data.get("quantity"),
            customer_id=data.get("customer_id"),
            status=data.get("status", "pending"),
        )
    except DuplicateOrderError as e:
        return error_response(str(e), 409)
    except ValueError as e:
        return error_response(str(e), 400)
    return jsonify(order), 201

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)
    if order is None:
        return error_response(f"Order with ID '{order_id}' not found.", 404)
    return jsonify(order), 200

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("Request body must be a JSON object.", 400)
    try:
        order = order_tracker.update_order_status(order_id, data.get("new_status"))
    except OrderNotFoundError as e:
        return error_response(str(e), 404)
    except ValueError as e:
        return error_response(str(e), 400)
    return jsonify(order), 200

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get("status")
    try:
        if status is None:
            orders = order_tracker.list_all_orders()
        else:
            orders = order_tracker.list_orders_by_status(status)
    except ValueError as e:
        return error_response(str(e), 400)
    return jsonify(orders), 200

if __name__ == '__main__':
    # Debug mode (reloader + interactive debugger) is opt-in: FLASK_DEBUG=1.
    # It must stay off when the app is reachable from outside, e.g. in Docker.
    app.run(host="0.0.0.0", port=8000, debug=os.environ.get("FLASK_DEBUG") == "1")
