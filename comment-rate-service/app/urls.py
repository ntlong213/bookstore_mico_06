from django.urls import path

from .views import BookRatingSummary, CommentRateListCreate, CommentReplyView


urlpatterns = [
    path('comments/', CommentRateListCreate.as_view(), name='comments_list_create'),
    path('comments/<int:comment_id>/reply/', CommentReplyView.as_view(), name='comments_reply'),
    path('ratings/<int:book_id>/summary/', BookRatingSummary.as_view(), name='book_rating_summary'),
]
