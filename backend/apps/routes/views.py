from django.db import models as django_models
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PriceCalendar, TravelRoute
from .serializers import PriceCalendarSerializer, TravelRouteSerializer


class TravelRouteViewSet(viewsets.ModelViewSet):
    serializer_class = TravelRouteSerializer

    def get_queryset(self):
        queryset = (
            TravelRoute.objects.prefetch_related(
                "stops__attraction", "bookings", "price_calendar"
            )
            .all()
        )
        status = self.request.query_params.get("status")
        city = self.request.query_params.get("city")
        if status:
            queryset = queryset.filter(status=status)
        if city:
            queryset = queryset.filter(city__icontains=city)
        return queryset

    @action(detail=True, methods=["get"], url_path="price-calendar")
    def price_calendar_list(self, request, pk=None):
        route = self.get_object()
        calendar_qs = route.price_calendar.all()
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date:
            calendar_qs = calendar_qs.filter(travel_date__gte=from_date)
        if to_date:
            calendar_qs = calendar_qs.filter(travel_date__lte=to_date)
        serializer = PriceCalendarSerializer(calendar_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="price-calendar")
    def price_calendar_create(self, request, pk=None):
        route = self.get_object()
        serializer = PriceCalendarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(route=route)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PriceCalendarViewSet(viewsets.ModelViewSet):
    serializer_class = PriceCalendarSerializer

    def get_queryset(self):
        queryset = PriceCalendar.objects.select_related("route").all()
        route_id = self.request.query_params.get("route_id")
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")
        available_only = self.request.query_params.get("available_only")
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if from_date:
            queryset = queryset.filter(travel_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(travel_date__lte=to_date)
        if available_only:
            now = timezone.now()
            queryset = queryset.filter(
                django_models.Q(registration_deadline__isnull=True)
                | django_models.Q(registration_deadline__gt=now)
            )
        return queryset
