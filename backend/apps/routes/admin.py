from django.contrib import admin

from .models import PriceCalendar, RouteStop, TravelRoute


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1


class PriceCalendarInline(admin.TabularInline):
    model = PriceCalendar
    extra = 1


@admin.register(TravelRoute)
class TravelRouteAdmin(admin.ModelAdmin):
    list_display = ("title", "city", "days", "status", "min_group_size", "max_group_size")
    list_filter = ("status", "city")
    search_fields = ("title", "city")
    inlines = [RouteStopInline, PriceCalendarInline]


@admin.register(PriceCalendar)
class PriceCalendarAdmin(admin.ModelAdmin):
    list_display = ("route", "travel_date", "base_cost", "inventory", "registration_deadline")
    list_filter = ("travel_date", "route")
    search_fields = ("route__title",)
    date_hierarchy = "travel_date"
