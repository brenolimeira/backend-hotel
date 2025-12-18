from rest_framework import serializers
from .models import Room, Guest, Booking

class RoomListSerializer(serializers.ModelSerializer):
    current_guests = serializers.IntegerField(read_only=True)
    occupied = serializers.BooleanField(read_only=True)

    class Meta:
        model = Room
        fields = [
            'id',
            'name',
            'guest_capacity',
            'current_guests',
            'occupied',
            'air_conditioning',
            'fan',
            'crib',
            'double_beds',
            'single_beds',
        ]

class RoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'name',
            'guest_capacity',
            'air_conditioning',
            'fan',
            'crib',
            'double_beds',
            'single_beds',
        ]

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    room = RoomListSerializer(read_only=True)
    guest = GuestSerializer(read_only=True, many=True)

    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        source='room',
        write_only=True
    )
    guest_ids = serializers.PrimaryKeyRelatedField(
        queryset=Guest.objects.all(),
        many=True,
        source='guest',
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'room',
            'room_id',
            'guest',
            'guest_ids',
            'check_in',
            'check_out',
            'status',
        ]