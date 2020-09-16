from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import WorkOrder


class WorkOrderAdmin(admin.ModelAdmin):
    list_display=['title', 'description', 'status', 'created_by', 'created_at', 'updated_at', 'assigned_to']
    list_display_links=list_display
    search_fields=list_display

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        obj.save()

admin.site.register(WorkOrder, WorkOrderAdmin)
