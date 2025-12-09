from django.db import models

# Create your models here.
from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=100)
    guest_capacity = models.IntegerField()
    air_conditioning = models.BooleanField(default=False)
    double_beds = models.IntegerField(default=0)
    single_beds = models.IntegerField(default=0)
    crib = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Guest(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    cpf = models.CharField(max_length=20, unique=True)
    rg = models.CharField(max_length=20, unique=True)
    birth_date = models.DateField(null=False, blank=False)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name="bookings")

    check_in = models.DateTimeField()
    check_out = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"Booking {self.id} - {self.room.name}"