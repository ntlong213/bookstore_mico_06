from django.db import models

class User(models.Model):
    ROLES = [
        ('customer', 'Customer'),
        ('staff',    'Staff'),
        ('manager',  'Manager'),
    ]
    username   = models.CharField(max_length=100, unique=True)
    email      = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    role       = models.CharField(max_length=20, choices=ROLES, default='customer')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"