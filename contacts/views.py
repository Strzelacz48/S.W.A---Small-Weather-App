from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import ContactForm
from .models import Contact

ALLOWED_SORT_FIELDS = {"last_name", "-last_name", "created_at", "-created_at"}
DEFAULT_SORT = "-created_at"


def _toggle(field, current_sort):
    """Return the query value that would reverse the sort direction for `field`."""
    return f"-{field}" if current_sort == field else field


def contact_list(request):
    sort = request.GET.get("sort", DEFAULT_SORT)
    if sort not in ALLOWED_SORT_FIELDS:
        sort = DEFAULT_SORT

    contacts = Contact.objects.select_related("status").order_by(sort)

    context = {
        "contacts": contacts,
        "current_sort": sort,
        "last_name_sort_link": _toggle("last_name", sort),
        "created_at_sort_link": _toggle("created_at", sort),
    }
    return render(request, "contacts/contact_list.html", context)


class ContactCreateView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "contacts/contact_form.html"
    success_url = reverse_lazy("contacts:list")


class ContactUpdateView(UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = "contacts/contact_form.html"
    success_url = reverse_lazy("contacts:list")