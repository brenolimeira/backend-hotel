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
    list_display = ("id", "name", "address", "cpf", "rg", "birth_date")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    list_editable = ("birth_date",)
    list_per_page = 10

admin.site.register(Guest, ListGuest)