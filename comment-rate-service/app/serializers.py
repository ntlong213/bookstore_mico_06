from rest_framework import serializers

from .models import CommentRate


class CommentRateSerializer(serializers.ModelSerializer):
    # Keep compatibility with frontend payload that sends/reads "content"
    content = serializers.CharField(source='comment', required=False, allow_blank=True)
    username = serializers.SerializerMethodField()

    class Meta:
        model = CommentRate
        fields = [
            'id',
            'customer_id',
            'book_id',
            'rating',
            'comment',
            'content',
            'reply',
            'replied_by',
            'replied_at',
            'created_at',
            'username',
        ]
        read_only_fields = ['id', 'created_at', 'replied_at', 'replied_by', 'username']

    def get_username(self, obj):
        return f"Customer {obj.customer_id}"
