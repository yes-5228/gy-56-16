from rest_framework.routers import DefaultRouter

from .views import PriceCalendarViewSet, TravelRouteViewSet

router = DefaultRouter()
router.register("price-calendar", PriceCalendarViewSet, basename="price-calendar")
router.register("", TravelRouteViewSet, basename="travel-route")

urlpatterns = router.urls
