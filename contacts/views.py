import csv
import io

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import CreateView, UpdateView

from .forms import ContactForm, ContactImportForm
from .models import Contact, ContactStatusChoices
from .weather import get_weather_for_city

CSV_COLUMNS = ("first_name", "last_name", "phone", "email", "city", "status")
REQUIRED_CSV_COLUMNS = set(CSV_COLUMNS)

ALLOWED_SORT_FIELDS = {"last_name", "-last_name", "created_at", "-created_at"}
DEFAULT_SORT = "-created_at"


def _toggle(field, current_sort):
    """Return the query value that would reverse the sort direction for `field`."""
    return f"-{field}" if current_sort == field else field


def _get_sorted_contacts(request):
    """Shared by contact_list and contact_export: validate ?sort= and return (contacts, sort)."""
    sort = request.GET.get("sort", DEFAULT_SORT)
    # If we pass unvalidated user input straight into order_by() — an
    # unknown/garbage field name would raise FieldError.
    if sort not in ALLOWED_SORT_FIELDS:
        sort = DEFAULT_SORT

    contacts = Contact.objects.select_related("status").order_by(sort)
    return contacts, sort


def contact_list(request):
    contacts, sort = _get_sorted_contacts(request)

    context = {
        "contacts": contacts,
        "current_sort": sort,
        "last_name_sort_link": _toggle("last_name", sort),
        "created_at_sort_link": _toggle("created_at", sort),
    }
    return render(request, "contacts/contact_list.html", context)


@require_GET
def contact_export(request):
    contacts, _ = _get_sorted_contacts(request)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="contacts.csv"'

    writer = csv.writer(response)
    writer.writerow(CSV_COLUMNS)
    for contact in contacts:
        writer.writerow([
            contact.first_name,
            contact.last_name,
            contact.phone,
            contact.email,
            contact.city,
            contact.status.name,
        ])

    return response


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


@require_POST
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    return redirect("contacts:list")


@require_GET
def contact_weather(request):
    city = request.GET.get("city", "").strip()
    if not city:
        return JsonResponse({"error": "city query param is required"}, status=400)

    weather = get_weather_for_city(city)
    if weather is None:
        return JsonResponse({"error": "weather unavailable for this city"}, status=502)

    return JsonResponse(weather)


def _import_contacts_from_csv(uploaded_file):
    """Import contacts from an uploaded CSV, skipping bad rows instead of failing the whole batch.

    Each row is validated through ContactForm, so it gets exactly the same
    rules as manually adding a contact (required fields, email format,
    unique phone/email) without duplicating that logic here.
    """
    decoded_file = io.TextIOWrapper(uploaded_file.file, encoding="utf-8-sig")
    reader = csv.DictReader(decoded_file)

    if not reader.fieldnames or not REQUIRED_CSV_COLUMNS.issubset(set(reader.fieldnames)):
        return {
            "error": f"CSV must have columns: {', '.join(sorted(REQUIRED_CSV_COLUMNS))}",
            "imported": 0,
            "skipped": [],
        }

    imported = 0
    skipped = []

    for row_number, row in enumerate(reader, start=2):  # row 1 is the header
        status_name = (row.get("status") or "").strip()
        status = ContactStatusChoices.objects.filter(name__iexact=status_name).first()
        if status is None:
            skipped.append((row_number, f"Unknown status '{status_name}'"))
            continue

        form = ContactForm(data={
            "first_name": (row.get("first_name") or "").strip(),
            "last_name": (row.get("last_name") or "").strip(),
            "phone": (row.get("phone") or "").strip(),
            "email": (row.get("email") or "").strip(),
            "city": (row.get("city") or "").strip(),
            "status": status.id,
        })
        if form.is_valid():
            form.save()
            imported += 1
        else:
            reasons = "; ".join(
                f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()
            )
            skipped.append((row_number, reasons))

    return {"error": None, "imported": imported, "skipped": skipped}


def contact_import(request):
    results = None
    if request.method == "POST":
        form = ContactImportForm(request.POST, request.FILES)
        if form.is_valid():
            results = _import_contacts_from_csv(form.cleaned_data["csv_file"])
    else:
        form = ContactImportForm()

    return render(request, "contacts/contact_import.html", {"form": form, "results": results})