from django.db import models

class Shipment(models.Model):
    STATUS = [
        ('preparing','Preparing'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
    ]
    order_id = models.IntegerField()
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='preparing')
    tracking_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)