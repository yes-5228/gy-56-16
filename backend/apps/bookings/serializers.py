from django.utils import timezone
from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    route_title = serializers.CharField(source="route.title", read_only=True)
    route_city = serializers.CharField(source="route.city", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    group_enrolled = serializers.IntegerField(source="route.enrolled_count", read_only=True)
    min_group_size = serializers.IntegerField(source="route.min_group_size", read_only=True)
    group_progress = serializers.IntegerField(source="route.group_progress", read_only=True)
    travel_base_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    travel_inventory = serializers.IntegerField(read_only=True)
    travel_remaining = serializers.IntegerField(read_only=True)
    registration_deadline = serializers.DateTimeField(read_only=True)
    date_enrolled = serializers.IntegerField(read_only=True)
    date_progress = serializers.IntegerField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "route",
            "route_title",
            "route_city",
            "contact_name",
            "phone",
            "party_size",
            "travel_date",
            "status",
            "status_label",
            "remark",
            "group_enrolled",
            "min_group_size",
            "group_progress",
            "travel_base_cost",
            "travel_inventory",
            "travel_remaining",
            "registration_deadline",
            "date_enrolled",
            "date_progress",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        route = instance.route
        travel_date = instance.travel_date
        min_size = route.min_group_size

        date_enrolled = sum(
            booking.party_size
            for booking in route.bookings.filter(travel_date=travel_date)
            .exclude(status="cancelled")
        )
        date_progress = min(round(date_enrolled / min_size * 100), 100) if min_size > 0 else 100

        price_calendar = route.price_calendar.filter(
            travel_date=travel_date
        ).first()
        if price_calendar:
            data["travel_base_cost"] = price_calendar.base_cost
            data["travel_inventory"] = price_calendar.inventory
            data["travel_remaining"] = price_calendar.remaining_inventory
            data["registration_deadline"] = price_calendar.registration_deadline
        else:
            data["travel_base_cost"] = route.base_cost
            data["travel_inventory"] = route.max_group_size
            data["travel_remaining"] = route.max_group_size - route.enrolled_count
            data["registration_deadline"] = None

        data["date_enrolled"] = date_enrolled
        data["date_progress"] = date_progress
        return data

    def validate(self, attrs):
        route = attrs.get("route")
        travel_date = attrs.get("travel_date")
        party_size = attrs.get("party_size", 1)

        price_calendar = route.price_calendar.filter(
            travel_date=travel_date
        ).first()

        if price_calendar:
            if price_calendar.registration_deadline and timezone.now() > price_calendar.registration_deadline:
                raise serializers.ValidationError(
                    {"travel_date": "该出行日期的报名已截止"}
                )

            if price_calendar.remaining_inventory < party_size:
                raise serializers.ValidationError(
                    {"party_size": f"库存不足，剩余名额为 {price_calendar.remaining_inventory}"}
                )
        else:
            remaining = route.max_group_size - route.enrolled_count
            if remaining < party_size:
                raise serializers.ValidationError(
                    {"party_size": f"名额不足，剩余名额为 {remaining}"}
                )

        return attrs
