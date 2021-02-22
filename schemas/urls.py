from rest_framework.routers import DefaultRouter
from .views import TableViewSet

router = DefaultRouter()
router.register('table', TableViewSet, basename="table")

urlpatterns = router.urls
