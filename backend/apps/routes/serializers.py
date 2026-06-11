from rest_framework import serializers

from apps.attractions.serializers import AttractionSerializer
from .models import PriceCalendar, RouteStop, TravelRoute


class RouteStopSerializer(serializers.ModelSerializer):
    attraction = AttractionSerializer(read_only=True)
    attraction_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RouteStop
        fields = ["id", "day", "order", "note", "attraction", "attraction_id"]


class PriceCalendarSerializer(serializers.ModelSerializer):
    enrolled_count = serializers.IntegerField(read_only=True)
    remaining_inventory = serializers.IntegerField(read_only=True)

    class Meta:
        model = PriceCalendar
        fields = [
            "id",
            "travel_date",
            "base_cost",
            "inventory",
            "remaining_inventory",
            "registration_deadline",
            "enrolled_count",
        ]


class TravelRouteSerializer(serializers.ModelSerializer):
    stops = RouteStopSerializer(many=True)
    price_calendar = PriceCalendarSerializer(many=True, required=False)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    ticket_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    estimated_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    enrolled_count = serializers.IntegerField(read_only=True)
    group_progress = serializers.IntegerField(read_only=True)

    class Meta:
        model = TravelRoute
        fields = [
            "id",
            "title",
            "city",
            "days",
            "transport",
            "hotel_level",
            "min_group_size",
            "max_group_size",
            "base_cost",
            "guide_fee",
            "ticket_total",
            "estimated_cost",
            "status",
            "status_label",
            "enrolled_count",
            "group_progress",
            "description",
            "stops",
            "price_calendar",
        ]

    def create(self, validated_data):
        stops_data = validated_data.pop("stops", [])
        price_calendar_data = validated_data.pop("price_calendar", [])
        route = TravelRoute.objects.create(**validated_data)
        self._sync_stops(route, stops_data)
        self._sync_price_calendar(route, price_calendar_data)
        return route

    def update(self, instance, validated_data):
        stops_data = validated_data.pop("stops", None)
        price_calendar_data = validated_data.pop("price_calendar", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if stops_data is not None:
            instance.stops.all().delete()
            self._sync_stops(instance, stops_data)
        if price_calendar_data is not None:
            instance.price_calendar.all().delete()
            self._sync_price_calendar(instance, price_calendar_data)
        return instance

    def _sync_stops(self, route, stops_data):
        for stop in stops_data:
            RouteStop.objects.create(
                route=route,
                attraction_id=stop["attraction_id"],
                day=stop.get("day", 1),
                order=stop.get("order", 1),
                note=stop.get("note", ""),
            )

    def _sync_price_calendar(self, route, price_calendar_data):
        for item in price_calendar_data:
            PriceCalendar.objects.create(
                route=route,
                travel_date=item["travel_date"],
                base_cost=item["base_cost"],
                inventory=item.get("inventory", 0),
                registration_deadline=item.get("registration_deadline"),
            )
