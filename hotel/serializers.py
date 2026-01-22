from rest_framework import serializers
from .models import Room, Guest, Booking
from django.utils.timezone import now

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
            'reservation_start',
            'reservation_end',
            'status',
        ]

    def validate(self, data):
        room = data['room']
        start = data['reservation_start']
        end = data['reservation_end']
        guests = data.get('guest', [])

        if start >= end:
            raise serializers.ValidationError(
                "A data final deve ser posterior à data inicial."
            )
        
        if start < now():
            raise serializers.ValidationError("Não é possível reservar no passado")

        conflict = Booking.objects.filter(
            room=room,
            status='active',
            reservation_start__lt=end,
            reservation_end__gt=start
        ).exists()

        if conflict:
            raise serializers.ValidationError({
                "reservation_period": "Já existe reserva nesse período"
            })

        if len(guests) > room.guest_capacity:
            raise serializers.ValidationError({
                "guest_ids": "Capacidade do quarto excedida."
            })

        return data