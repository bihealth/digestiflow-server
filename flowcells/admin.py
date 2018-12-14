from django.contrib import admin

from .models import FlowCell, Library, LaneIndexHistogram, Message, KnownIndexContamination

# Register your models here.
admin.site.register(FlowCell)
admin.site.register(Library)
admin.site.register(LaneIndexHistogram)
admin.site.register(Message)
admin.site.register(KnownIndexContamination)
