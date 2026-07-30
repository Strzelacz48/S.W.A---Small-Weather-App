from django.shortcuts import render


def contact_list(request):
    return render(request, "contacts/contact_list.html")
