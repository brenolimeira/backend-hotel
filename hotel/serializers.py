from rest_framework import serializers
from .models import Room, Guest, Booking

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    guest = GuestSerializer(read_only=True, many=True)

    class Meta:
        model = Booking
        fields = '__all__'