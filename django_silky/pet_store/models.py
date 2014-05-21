from django.db import models
from django.db.models import DateTimeField, CharField, ForeignKey
from django.utils import timezone


class Pet(models.Model):
    date_of_birth = DateTimeField(default=timezone.now, db_index=True)
    name = CharField(max_length=100)
    owner = ForeignKey('Owner')


class Owner(models.Model):
    name = CharField(max_length=200)


class Dog(Pet):
    breed = CharField(max_length=200)


class Cat(Pet):
    pass


