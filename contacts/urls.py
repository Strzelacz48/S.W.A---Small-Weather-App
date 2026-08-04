from django.urls import path

from . import views

app_name = "contacts"

urlpatterns = [
    path("", views.contact_list, name="list"),
    path("add/", views.ContactCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", views.ContactUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.contact_delete, name="delete"),
    path("weather/", views.contact_weather, name="weather"),
]
