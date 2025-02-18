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


admin.site.register(AirplaneType)
admin.site.register(SeatConfiguration)
admin.site.register(Flight)
admin.site.register(Ticket)
