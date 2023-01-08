from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _("Categories")


class Product(models.Model):
    photo = models.ImageField(upload_to='products')

    class Meta:
        abstract = True


class Blind(Product):
    name = models.TextField()
    child_safe = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=~models.Q(name=""),
                name="unique_name_if_provided",
            ),
        ]
