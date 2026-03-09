from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from django.db.models import Count, Q, BooleanField, Case, When, Value
from .models import Room, Guest, Booking
from .serializers import RoomListSerializer, RoomCreateSerializer, GuestSerializer, BookingSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

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
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def destroy(self, request, *args, **kwargs):
        guest = self.get_object()

        # verifica se existe booking ativa
        if guest.bookings.filter(status='active').exists():
            raise ValidationError("Este hóspede possui hospedagens ativas e não pode ser excluído.")

        return super().destroy(request, *args, **kwargs)

class BookingViewSet(viewsets.ModelViewSet):
        queryset = Booking.objects.all()
        serializer_class = BookingSerializer

        def get_queryset(self):
            qs = super().get_queryset()
            params = self.request.query_params

            status_param = params.get("status")
            room_id = params.get("room")

            if status_param:
                status_list = [s.strip().lower() for s in status_param.split(",")]
                qs = qs.filter(status__in=status_list)

            if room_id:
                qs = qs.filter(room_id=room_id)

            return qs

        @action(detail=False, methods=['get'], url_path='room/(?P<room_id>[^/.]+)')
        def by_room(self, request, room_id=None):
            print(self.request.query_params)
            bookings = self.get_queryset().filter(room_id=room_id)
            serializer = self.get_serializer(bookings, many=True)
            return Response(serializer.data)
        
        @action(detail=False, methods=["get"], url_path="blocked-dates/(?P<room_id>[^/.]+)")
        def blocked_dates(self, request, room_id=None):
            bookings = Booking.objects.filter(
                room_id=room_id,
                status__in=["active", "reserved"]
            ).values('reservation_start', 'reservation_end')

            return Response(bookings)
        
        @action(detail=True, methods=['post'])
        def cancel(self, request, pk=None):
            booking = self.get_object()

            if booking.status in ["completed", "canceled"]:
                return Response(
                    {"error": "Reserva não pode ser cancelada"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            booking.status = "canceled"
            booking.save()

            serializer = self.get_serializer(booking)
            return Response(serializer.data)
        
        @action(detail=True, methods=['post'])
        def checkout(self, request, pk=None):
            booking = self.get_object()

            if booking.status != "active":
                return Response(
                    {"error": "Reserva já finalizada"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            booking.check_out = timezone.now()
            booking.status = "completed"
            booking.save()

            serializer = self.get_serializer(booking)
            return Response(serializer.data)

        @action(detail=True, methods=['post'])
        def checkin(self, request, pk=None):
            booking = self.get_object()

            if booking.status != "reserved":
                return Response(
                    {"error": "Só reservas podem fazer check-in"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            booking.check_in = timezone.now()
            booking.status = "active"
            booking.save()

            serializer = self.get_serializer(booking)
            return Response(serializer.data)

class AuthViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def register(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response({"error": "Todos os campos são obrigatórios"})

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Usuário já existe"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )   
        user.save()

        
        return Response({"message": "Usuário registrado"})
    
    @action(detail=False, methods=['post'])
    def login(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Nome de usuário e senha são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })
        
        return Response({"error": "Credenciais inválidas"}, status=401)