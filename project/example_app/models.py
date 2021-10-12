from django.db import models

# Create your models here.
from django.db.models import TextField, BooleanField, ImageField


class Product(models.Model):
    photo = ImageField(upload_to="products")

    class Meta:
        abstract = True


class Blind(Product):
    name = TextField()
    child_safe = BooleanField(default=False)

    def __str__(self):
        return self.name
