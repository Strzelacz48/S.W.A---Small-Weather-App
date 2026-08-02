from django.contrib import admin

from .models import Contact, ContactStatusChoices


@admin.register(ContactStatusChoices)
class ContactStatusChoicesAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "phone", "email", "city", "status", "created_at"]
    list_filter = ["status", "city"]
    search_fields = ["first_name", "last_name", "phone", "email"]
