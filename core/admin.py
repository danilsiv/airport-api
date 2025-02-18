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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)



admin.site.register(City)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(Role)
admin.site.register(CrewMember)
admin.site.register(CrewGroup)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(SeatConfiguration)
admin.site.register(Flight)
admin.site.register(Order)
admin.site.register(Ticket)
