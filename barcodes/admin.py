from django.contrib import admin

from .models import BarcodeSet, BarcodeSetEntry

# Register your models here.
admin.site.register(BarcodeSet)
admin.site.register(BarcodeSetEntry)
