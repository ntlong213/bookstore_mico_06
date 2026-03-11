from django.db import models

class Payment(models.Model):
    STATUS = [('pending','Pending'),('success','Success'),('failed','Failed')]
    order_id = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, default='cash')
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)