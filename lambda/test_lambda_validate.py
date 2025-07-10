from lambda_validate_order import lambda_handler
import uuid
from datetime import datetime

event = {
    "order_id": str(uuid.uuid4()),
    "user_id": "test_user",
    "amount": 1500.00,
    "items": [{"product_id": "abc123", "quantity": 2}],
    "timestamp": datetime.utcnow().isoformat()
}

lambda_handler(event)
