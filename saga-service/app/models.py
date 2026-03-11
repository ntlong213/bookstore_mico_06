from django.db import models

class SagaTransaction(models.Model):
    STATUS = [
        ('started','Started'),
        ('payment_reserved','Payment Reserved'),
        ('shipping_reserved','Shipping Reserved'),
        ('completed','Completed'),
        ('compensating','Compensating'),
        ('failed','Failed'),
    ]
    order_id = models.IntegerField()
    customer_id = models.IntegerField()
    status = models.CharField(max_length=30, choices=STATUS, default='started')
    payment_id = models.IntegerField(null=True, blank=True)
    shipment_id = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)