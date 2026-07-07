from django.db import models
from taggit.managers import TaggableManager
from products.default.models import Product

class Genre(models.Model):
    name = models.CharField(max_length=500)
    class Meta:
        db_table = "genre"
    def __str__(self):
        return self.name

class Author(models.Model):
    fullname = models.CharField(max_length=500)
    class Meta:
        db_table = "author"
    def __str__(self):
        return self.fullname

class Publisher(models.Model):
    name = models.CharField(max_length=500)
    class Meta:
        db_table = "publisher"
    def __str__(self):
        return self.name

class Book(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DEACTIVATED", "Deactivated"),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="books",
    )
    title = models.CharField(max_length=500)
    synopsis = models.TextField()
    isbn = models.CharField(max_length=17, unique=True)
    release_date = models.DateField(null=True, blank=True)
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.PROTECT,
        related_name="books"
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books"
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.PROTECT,
        related_name="books"
    )
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
