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
    list_display = ("user", "created_at")


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    inlines = (SeatConfigurationInline,)
    list_display = ("model_name", "type")
    search_fields = ("model_name", "type__name")


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


@admin.register(CrewGroup)
class CrewGroupAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "pilots":
            kwargs["queryset"] = CrewMember.objects.filter(role__name="Pilot")
        elif db_field.name == "stewards":
            kwargs["queryset"] = CrewMember.objects.filter(role__name="Steward")
        elif db_field.name == "technicians":
            kwargs["queryset"] = CrewMember.objects.filter(role__name="Technician")
        elif db_field.name == "additional_staff":
            kwargs["queryset"] = CrewMember.objects.exclude(
                role__name__in=("Pilot", "Steward", "Technician")
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(SeatConfiguration)
class SeatConfigurationAdmin(admin.ModelAdmin):
    list_display = ("seats_class", "airplane", "rows", "seats_in_row")
    search_fields = ("airplane__model_name",)
    list_filter = ("seats_class",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("flight_number", "route", "airplane", "status")
    search_fields = ("flight_number",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("passenger_full_name", "flight__route", "seat_class")
    search_fields = ("flight__flight_number",)
    list_filter = ("seat_class",)

    def passenger_full_name(self, obj) -> str:
        return f"{obj.passenger_first_name} {obj.passenger_last_name}"

    passenger_full_name.short_description = "passenger_full_name"
