from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hotel.views import RoomViewSet, GuestViewSet, BookingViewSet, AuthViewSet

router = DefaultRouter()
router.register('rooms', RoomViewSet, basename='rooms')
router.register('guests', GuestViewSet, basename='guests')
router.register('bookings', BookingViewSet, basename='bookings')
router.register('auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]