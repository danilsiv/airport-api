from django.contrib import admin
from core.models import (
    City,
    Airport,
    Route,
    Role,
    CrewMember,
    CrewGroup,
    AirplaneType,
    Airplane,
    SeatConfiguration,
    Flight,
    Order,
    Ticket,
)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


class SeatConfigurationInline(admin.TabularInline):
    model = SeatConfiguration
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    inlines = (SeatConfigurationInline,)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name", "country")


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "iata_code", "city")
    search_fields = ("name", "iata_code", "city__name")
    list_filter = ("city__country",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    search_fields = ("source__city__name", "destination__city__name")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role")
    list_filter = ("role__name",)

    def full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "full_name"


admin.site.register(CrewGroup)
admin.site.register(AirplaneType)
admin.site.register(SeatConfiguration)
admin.site.register(Flight)
admin.site.register(Ticket)
