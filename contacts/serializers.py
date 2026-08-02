from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id', 'first_name', 'last_name', 'phone', 'email',
            'city', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
