from rest_framework.views import APIView
from rest_framework.response import Response
import requests

COMMENT_SERVICE_URL = "http://comment-rate-service:8000"
BOOK_SERVICE_URL = "http://book-service:8000"

class RecommendBooks(APIView):
    def get(self, request, customer_id):
        """Recommend sách dựa trên rating cao nhất"""
        try:
            # Lấy tất cả ratings
            ratings_r = requests.get(f"{COMMENT_SERVICE_URL}/comments/", timeout=5)
            all_ratings = ratings_r.json()
            if not isinstance(all_ratings, list):
                all_ratings = all_ratings.get('results', []) if isinstance(all_ratings, dict) else []

            # Lọc bỏ sách customer đã đọc
            customer_books = {r['book_id'] for r in all_ratings if r['customer_id'] == customer_id}

            # Tính điểm trung bình từng sách
            book_scores = {}
            for r in all_ratings:
                if r['book_id'] not in customer_books:
                    if r['book_id'] not in book_scores:
                        book_scores[r['book_id']] = []
                    book_scores[r['book_id']].append(r['rating'])

            avg_scores = {bid: sum(scores)/len(scores) for bid, scores in book_scores.items()}
            top_books = sorted(avg_scores, key=avg_scores.get, reverse=True)[:5]

            # Lấy thông tin sách
            books_r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
            all_books = {b['id']: b for b in books_r.json()}
            recommended = [all_books[bid] for bid in top_books if bid in all_books]

            return Response({
                "customer_id": customer_id,
                "recommendations": recommended
            })
        except Exception as e:
            # Fallback: trả về sách ngẫu nhiên
            try:
                books_r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
                books_data = books_r.json()
                if not isinstance(books_data, list):
                    books_data = books_data.get('results', []) if isinstance(books_data, dict) else []
                return Response({
                    "customer_id": customer_id,
                    "recommendations": books_data[:5],
                    "note": "Fallback recommendations"
                })
            except:
                return Response({"error": "Service unavailable"}, status=503)