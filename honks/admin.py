from django.contrib import admin
from honks.models import Honk


@admin.register(Honk)
class HonkAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'created_at',
        'user',
        'content',
    )
