from django.db import models

class CommentRate(models.Model):
    customer_id = models.IntegerField()
    book_id = models.IntegerField()
    rating = models.IntegerField(choices=[(i,i) for i in range(1,6)])
    comment = models.TextField(blank=True)
    reply = models.TextField(blank=True, default='')
    replied_by = models.CharField(max_length=100, blank=True, default='')
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer_id', 'book_id')
        ordering = ['-created_at']