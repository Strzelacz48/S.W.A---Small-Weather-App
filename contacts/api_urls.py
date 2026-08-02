from rest_framework.routers import DefaultRouter

from .api_views import ContactViewSet

router = DefaultRouter()
router.register('contacts', ContactViewSet, basename='contact')

urlpatterns = router.urls