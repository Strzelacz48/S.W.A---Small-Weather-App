from django import forms

from .models import Contact

TAILWIND_INPUT_CLASSES = (
    "w-full rounded-md border border-gray-300 px-3 py-2 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500"
)


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["first_name", "last_name", "phone", "email", "city", "status"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": TAILWIND_INPUT_CLASSES}),
            "last_name": forms.TextInput(attrs={"class": TAILWIND_INPUT_CLASSES}),
            "phone": forms.TextInput(attrs={"class": TAILWIND_INPUT_CLASSES}),
            "email": forms.EmailInput(attrs={"class": TAILWIND_INPUT_CLASSES}),
            "city": forms.TextInput(attrs={"class": TAILWIND_INPUT_CLASSES}),
            "status": forms.Select(attrs={"class": TAILWIND_INPUT_CLASSES}),
        }


class ContactImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV file",
        widget=forms.FileInput(attrs={"class": TAILWIND_INPUT_CLASSES, "accept": ".csv"}),
    )