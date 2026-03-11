import requests
import logging

logger = logging.getLogger(__name__)

ORDER_SERVICE_URL   = "http://order-service:8000"
PAY_SERVICE_URL     = "http://pay-service:8000"
SHIP_SERVICE_URL    = "http://ship-service:8000"
CART_SERVICE_URL    = "http://cart-service:8000"
BOOK_SERVICE_URL    = "http://book-service:8000"

class OrderSaga:
    def __init__(self, saga_record):
        self.saga = saga_record

    def execute(self, order_data):
        """
        Saga Steps:
        1. Create Order (Pending)
        2. Reserve Payment
        3. Reserve Shipping
        4. Confirm Order
        Compensate on failure
        """
        order_id = None
        payment_id = None

        try:
            # ── Step 1: Create Order ──────────────────
            logger.info(f"[SAGA] Step 1: Creating order")
            r = requests.post(f"{ORDER_SERVICE_URL}/orders/create-pending/",
                json=order_data, timeout=5)
            if r.status_code != 201:
                raise Exception(f"Order creation failed: {r.text}")
            order_id = r.json()['id']
            self.saga.order_id = order_id
            self.saga.status = 'started'
            self.saga.save()

            # ── Step 2: Reserve Payment ───────────────
            logger.info(f"[SAGA] Step 2: Reserving payment for order {order_id}")
            r = requests.post(f"{PAY_SERVICE_URL}/payments/reserve/", json={
                "order_id": order_id,
                "amount": order_data.get('total_amount', 0),
                "method": order_data.get('payment_method', 'cash')
            }, timeout=5)
            if r.status_code != 201:
                raise Exception(f"Payment reservation failed: {r.text}")
            payment_id = r.json()['id']
            self.saga.payment_id = payment_id
            self.saga.status = 'payment_reserved'
            self.saga.save()

            # ── Step 3: Reserve Shipping ──────────────
            logger.info(f"[SAGA] Step 3: Reserving shipment for order {order_id}")
            r = requests.post(f"{SHIP_SERVICE_URL}/shipments/reserve/", json={
                "order_id": order_id,
                "address": order_data.get('shipping_address', '')
            }, timeout=5)
            if r.status_code != 201:
                raise Exception(f"Shipping reservation failed: {r.text}")
            shipment_id = r.json()['id']
            self.saga.shipment_id = shipment_id
            self.saga.status = 'shipping_reserved'
            self.saga.save()

            # ── Step 4: Confirm Order ─────────────────
            logger.info(f"[SAGA] Step 4: Confirming order {order_id}")
            requests.put(f"{ORDER_SERVICE_URL}/orders/{order_id}/",
                json={"status": "confirmed"}, timeout=5)
            requests.post(f"{PAY_SERVICE_URL}/payments/{payment_id}/confirm/",
                timeout=5)
            requests.put(f"{SHIP_SERVICE_URL}/shipments/{shipment_id}/",
                json={"status": "preparing"}, timeout=5)

            self.saga.status = 'completed'
            self.saga.save()
            logger.info(f"[SAGA] ✅ Order {order_id} completed successfully")
            return {"success": True, "order_id": order_id, "saga_id": self.saga.id}

        except Exception as e:
            logger.error(f"[SAGA] ❌ Failed: {str(e)}")
            self.saga.error_message = str(e)
            self.saga.status = 'compensating'
            self.saga.save()
            # Compensate
            self._compensate(order_id, payment_id)
            return {"success": False, "error": str(e)}

    def _compensate(self, order_id, payment_id):
        """Rollback các bước đã thực hiện"""
        logger.warning(f"[SAGA] 🔄 Compensating transaction...")
        if payment_id:
            try:
                requests.post(f"{PAY_SERVICE_URL}/payments/{payment_id}/cancel/",
                    timeout=5)
                logger.info(f"[SAGA] Payment {payment_id} cancelled")
            except:
                pass
        if order_id:
            try:
                requests.put(f"{ORDER_SERVICE_URL}/orders/{order_id}/",
                    json={"status": "cancelled"}, timeout=5)
                logger.info(f"[SAGA] Order {order_id} cancelled")
            except:
                pass
        self.saga.status = 'failed'
        self.saga.save()