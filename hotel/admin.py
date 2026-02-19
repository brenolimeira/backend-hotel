from django.contrib import admin

from hotel.models import Room, Guest, Booking

class ListRoom(admin.ModelAdmin):
    list_display = ("id", "name", "guest_capacity", "air_conditioning", "double_beds", "single_beds", "crib")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    list_filter = ("air_conditioning", "crib")
    list_editable = ("double_beds", "single_beds")
    list_per_page = 10

admin.site.register(Room, ListRoom)

class ListGuest(admin.ModelAdmin):
    list_display = ("id", "name", "cpf", "rg", "birth_date", "phone")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    list_editable = ("birth_date", "phone")
    list_per_page = 10

admin.site.register(Guest, ListGuest)

class ListBooking(admin.ModelAdmin):
    list_display = ("id", "room", "check_in", "check_out", "status", "reservation_start", "reservation_end")
    list_display_links = ("id", "room")
    search_fields = ("room", "guest")
    list_editable = ("status",)
    filter_horizontal = ("guest",)
    list_per_page = 10

admin.site.register(Booking, ListBooking)