from django.contrib import admin

from .models import (
    FileBox,
    FileBoxAuditEntry,
)

# Register your models here.
admin.site.register((FileBox, FileBoxAuditEntry))
