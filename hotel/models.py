from django.db import models

# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError

class Room(models.Model):
    name = models.CharField(max_length=100)
    guest_capacity = models.IntegerField()
    air_conditioning = models.BooleanField(default=False)
    fan = models.BooleanField(default=False)
    double_beds = models.IntegerField(default=0)
    single_beds = models.IntegerField(default=0)
    crib = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Guest(models.Model):
    name = models.CharField(max_length=100)
    cpf = models.CharField(max_length=20, unique=True)
    rg = models.CharField(max_length=20, unique=True)
    birth_date = models.DateField(null=False, blank=False)
    phone = models.CharField(max_length=14, unique=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('reserved', 'Reserved')
    ]

    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="bookings")
    guest = models.ManyToManyField(Guest, related_name="bookings")

    reservation_start = models.DateTimeField()
    reservation_end = models.DateTimeField()

    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reserved')

    def __str__(self):
        return f"Booking {self.id} - {self.room.name}"