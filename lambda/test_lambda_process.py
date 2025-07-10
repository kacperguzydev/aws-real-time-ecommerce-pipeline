from lambda_process_stream import lambda_handler
import base64
import json
import uuid
from datetime import datetime

order = {
    "order_id": str(uuid.uuid4()),
    "user_id": "test_user",
    "amount": 1500.00,
    "items": [{"product_id": "abc123", "quantity": 2}],
    "timestamp": datetime.utcnow().isoformat()
}

encoded_data = base64.b64encode(json.dumps(order).encode("utf-8")).decode("utf-8")

event = {
    "Records": [
        {
            "kinesis": {
                "data": encoded_data
            }
        }
    ]
}

lambda_handler(event)
