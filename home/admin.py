from django.contrib import admin
from .models import Contact,CustomUser


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name","email","phone","content","timestamp")
    readonly_fields=("name","email","phone","content","timestamp")
    list_filter=("timestamp",)
    ordering = ('-timestamp',)
    search_fields = ("name","email","phone")

admin.site.register(CustomUser)
