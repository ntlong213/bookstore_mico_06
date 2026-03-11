from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    # ── Thông tin cơ bản ──────────────────────
    title       = models.CharField(max_length=500)
    slug        = models.SlugField(max_length=500, unique=True, blank=True)
    author      = models.CharField(max_length=255)
    publisher   = models.CharField(max_length=255, blank=True)
    isbn        = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # ── Phân loại ────────────────────────────
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    language    = models.CharField(max_length=50, default='Vietnamese')
    tags        = models.CharField(max_length=500, blank=True, help_text="Comma separated tags")

    # ── Nội dung ─────────────────────────────
    description = models.TextField(blank=True)
    pages       = models.IntegerField(null=True, blank=True)
    publish_year= models.IntegerField(null=True, blank=True)

    # ── Ảnh bìa ──────────────────────────────
    cover_image = models.URLField(max_length=1000, blank=True,
        default='https://via.placeholder.com/300x400?text=No+Cover')

    # ── Giá & Kho ────────────────────────────
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock       = models.IntegerField(default=0)
    sold_count  = models.IntegerField(default=0)

    # ── Đánh giá ─────────────────────────────
    avg_rating  = models.FloatField(default=0.0)
    review_count= models.IntegerField(default=0)

    # ── Trạng thái ───────────────────────────
    is_active   = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return 0