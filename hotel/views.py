from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Count, Q, BooleanField, Case, When, Value
from django.utils import timezone
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
    
    def destroy(self, request, *args, **kwargs):
        room = self.get_object()

        # impede excluir quarto com reservas ativas
        if room.bookings.filter(status='active').exists():
            raise ValidationError("Este quarto possui hospedagens ativas e não pode ser excluído.")

        return super().destroy(request, *args, **kwargs)

class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def destroy(self, request, *args, **kwargs):
        guest = self.get_object()

        # verifica se existe booking ativa
        if guest.bookings.filter(status='active').exists():
            raise ValidationError("Este hóspede possui hospedagens ativas e não pode ser excluído.")

        return super().destroy(request, *args, **kwargs)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @action(detail=False, methods=['get'], url_path='room/(?P<room_id>[^/.]+)')
    def by_room(self, request, room_id=None):
        bookings = Booking.objects.filter(room_id=room_id)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="blocked-dates/(?P<room_id>[^/.]+)")
    def blocked_dates(self, request, room_id=None):
        bookings = Booking.objects.filter(
            room_id=room_id,
            status='active'
        ).values('reservation_start', 'reservation_end')

        return Response(bookings)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if booking.status == 'canceled':
            return Response(
                {"detail": "Reserva já está cancelada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.status == 'completed':
            return Response(
                {"detail": "Reserva já foi finalizada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'canceled'
        booking.save()

        return Response(
            {"detail": "Reserva cancelada com sucesso."},
            status=status.HTTP_200_OK
        )