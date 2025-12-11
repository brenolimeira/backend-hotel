from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Room, Guest, Booking
from .serializers import RoomSerializer, GuestSerializer, BookingSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

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