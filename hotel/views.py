from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, BooleanField, Case, When, Value
from .models import Room, Guest, Booking
from .serializers import RoomListSerializer, RoomCreateSerializer, GuestSerializer, BookingSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RoomListSerializer
        return RoomCreateSerializer

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return (
                Room.objects
                .annotate(
                    current_guests=Count(
                        'bookings__guest',
                        filter=Q(bookings__status='active'),
                        distinct=True
                    )
                )
                .annotate(
                    occupied=Case(
                        When(current_guests__gt=0, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField()
                    )
                )
            )
        return Room.objects.all()

class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @action(detail=False, methods=['get'], url_path='room/(?P<room_id>[^/.]+)')
    def by_room(self, request, room_id=None):
        bookings = Booking.objects.filter(room_id=room_id)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)