from django.db import models
from taggit.managers import TaggableManager


class Author(models.Model):
    fullname = models.CharField(max_length=500)

    class Meta:
        db_table = "author"

    def __str__(self):
        return self.fullname


class Book(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DEACTIVATED", "Deactivated"),
    ]

    title = models.CharField(max_length=500)
    synopsis = models.TextField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.18)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    release_date = models.DateField(null=True, blank=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books"
    )
    tags = TaggableManager(blank=True)
    class Meta:
        db_table = "book"

    def __str__(self):
        return self.title

class BookImage(models.Model):
    IMAGE_TYPES = [
        ("FRONT_COVER", "Front Cover"),
        ("BACK_COVER", "Back Cover"),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.CharField(max_length=1000)

    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPES
    )

    class Meta:
        db_table = "book_image"
        constraints = [
            models.UniqueConstraint(
                fields=["book", "image_type"],
                name="unique_image_type_per_book"
            )
        ]

    def __str__(self):
        return f"{self.book.title} - {self.get_image_type_display()}"
    